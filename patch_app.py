import re
import json

with open('web/app.py', 'r') as f:
    text = f.read()

# 1. Update get_xray_version
text = re.sub(
    r'def get_xray_version.*?(?=\ndef is_xray_running)',
    '''def get_xray_version() -> str:
    try:
        import subprocess
        res = subprocess.run(["/usr/local/bin/xray", "version"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            lines = res.stdout.split('\\n')
            if lines:
                import re as rex
                m = rex.search(r"Xray\s+([\d\.]+)", lines[0])
                if m: return m.group(1)
                return lines[0].strip()
    except Exception:
        pass
    return "Unknown"
''',
    text, flags=re.DOTALL
)

# 2. Update _load_store
text = re.sub(
    r'def _load_store.*?(?=\ndef _save_store)',
    '''def _load_store() -> dict:
    from uuid import uuid4
    if not CONFIGS_PATH.exists():
        default_item = dict(DEFAULTS)
        default_item["id"] = str(uuid4())
        default_item["enabled"] = True
        store = {"configs": [default_item]}
        CONFIGS_PATH.write_text(json.dumps(store, indent=2), encoding="utf-8")
        return store
    try:
        store = json.loads(CONFIGS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        store = {"configs": []}
    
    migrated = False
    for c in store.get("configs", []):
        if "enabled" not in c:
            c["enabled"] = (c.get("id") == store.get("active_id"))
            migrated = True
    if migrated:
        _save_store(store)
    return store
''',
    text, flags=re.DOTALL, count=1
)

# 3. Update build_config
text = re.sub(
    r'def build_config\(form: dict\) -> dict.*?(?=\ndef read_config_text)',
    '''def build_config(configs: list) -> dict:
    inbounds = []
    for form in configs:
        if not form.get("enabled", True):
            continue

        domain = form["domain"]
        ws_enabled = form["ws_enabled"]
        tls_enabled = form["tls_enabled"]
        protocol = form.get("protocol", "vless")
        cid = form.get("id", "")

        if ws_enabled:
            ws_client = {"id": form["ws_uuid"], "level": 0, "email": form["ws_email"]}
            if protocol == "vmess": ws_client["alterId"] = 0
            inbounds.append({
                "port": form["ws_port"],
                "listen": "0.0.0.0",
                "protocol": protocol,
                "tag": f"ws-{cid}",
                "settings": {"clients": [ws_client], **({"decryption": "none"} if protocol == "vless" else {})},
                "streamSettings": {"network": "ws", "wsSettings": {"path": form["ws_path"], "host": domain}},
                "sniffing": {"enabled": True, "destOverride": ["http", "tls"], "metadataOnly": False}
            })

        if tls_enabled:
            tls_client = {"id": form["tls_uuid"], "level": 0, "email": form["tls_email"]}
            if protocol == "vmess": tls_client["alterId"] = 0
            inbounds.append({
                "port": form["tls_port"],
                "listen": "0.0.0.0",
                "protocol": protocol,
                "tag": f"wstls-{cid}",
                "settings": {"clients": [tls_client], **({"decryption": "none"} if protocol == "vless" else {})},
                "streamSettings": {
                    "network": "ws",
                    "security": "tls",
                    "tlsSettings": {
                        "certificates": [{"certificateFile": form["tls_cert"], "keyFile": form["tls_key"]}],
                        "minVersion": "1.2", "maxVersion": "1.3", "allowInsecure": False,
                        "cipherSuites": "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256",
                        "alpn": ["http/1.1"]
                    },
                    "wsSettings": {"path": form["tls_path"], "host": domain}
                },
                "sniffing": {"enabled": True, "destOverride": ["http", "tls"], "metadataOnly": False}
            })

    return {
        "log": {"loglevel": "info", "access": "/data/logs/access.log", "error": "/data/logs/error.log"},
        "inbounds": inbounds,
        "outbounds": [{"protocol": "freedom", "settings": {}, "tag": "direct"}, {"protocol": "blackhole", "settings": {}, "tag": "blocked"}],
        "routing": {"domainStrategy": "IPOnDemand", "rules": [{"type": "field", "domain": ["geosite:private"], "outboundTag": "blocked"}, {"type": "field", "ip": ["geoip:private"], "outboundTag": "blocked"}]}
    }
''',
    text, flags=re.DOTALL, count=1
)

# 4. Replace index route
text = re.sub(
    r'@app\.route\("/"\)\ndef index\(\):.*?(?=@app\.route\("/save", methods=\["POST"\]\))',
    '''@app.route("/")
def index():
    status = get_status()
    store = _load_store()
    edit_id = request.args.get("edit")
    
    if edit_id == "new":
        form_state = dict(DEFAULTS)
    elif edit_id:
        found = _find_config(store, edit_id)
        if found:
            form_state = dict(found)
            if "protocol" not in form_state:
                form_state["protocol"] = DEFAULTS["protocol"]
        else:
            form_state = dict(DEFAULTS)
    else:
        form_state = dict(DEFAULTS)

    active_count = 0
    configs = store.get("configs", [])
    for c in configs:
        if c.get("enabled", True):
            active_count += 1
            
        c["links"] = []
        proto = c.get("protocol", "vless")
        name = c.get("name", "Config")
        domain = c.get("domain", DOMAIN)
        if c.get("tls_enabled"):
            url = _vless_link(name, domain, c["tls_port"], c["tls_uuid"], c["tls_path"], True) if proto == "vless" else _vmess_link(name, domain, c["tls_port"], c["tls_uuid"], c["tls_path"], True)
            c["links"].append({"label": "WS + TLS", "url": url, "qr": _qr_data(url)})
        if c.get("ws_enabled"):
            url = _vless_link(name, domain, c["ws_port"], c["ws_uuid"], c["ws_path"], False) if proto == "vless" else _vmess_link(name, domain, c["ws_port"], c["ws_uuid"], c["ws_path"], False)
            c["links"].append({"label": "WS (No TLS)", "url": url, "qr": _qr_data(url)})

    message = request.args.get("message")
    error = request.args.get("error")
    return render_template(
        "index.html",
        status=status,
        form=form_state,
        store=store,
        active_count=active_count,
        configs=configs,
        edit_id=edit_id,
        summary=_summary,
        message=message,
        error=error,
    )
''',
    text, flags=re.DOTALL, count=1
)

# 5. replace save, activate to toggle, and bootstrap
text = re.sub(
    r'@app\.route\("/save", methods=\["POST"\]\)\ndef save\(\):.*?(?=@app\.route\("/new"\))',
    '''@app.route("/save", methods=["POST"])
def save():
    store = _load_store()
    edit_id = request.form.get("edit_id")
    if edit_id == "new": edit_id = None
    from uuid import uuid4
    form = {
        "id": edit_id or str(uuid4()),
        "name": request.form.get("name", DEFAULTS["name"]).strip() or DEFAULTS["name"],
        "domain": request.form.get("domain", DEFAULTS["domain"]).strip() or DEFAULTS["domain"],
        "protocol": request.form.get("protocol", DEFAULTS["protocol"]).strip() or DEFAULTS["protocol"],
        "ws_enabled": request.form.get("ws_enabled") == "on",
        "tls_enabled": request.form.get("tls_enabled") == "on",
        "ws_path": request.form.get("ws_path", DEFAULTS["ws_path"]).strip() or DEFAULTS["ws_path"],
        "tls_path": request.form.get("tls_path", DEFAULTS["tls_path"]).strip() or DEFAULTS["tls_path"],
        "ws_uuid": request.form.get("ws_uuid", "").strip() or str(uuid4()),
        "tls_uuid": request.form.get("tls_uuid", "").strip() or str(uuid4()),
        "ws_email": request.form.get("ws_email", DEFAULTS["ws_email"]).strip(),
        "tls_email": request.form.get("tls_email", DEFAULTS["tls_email"]).strip(),
        "tls_cert": request.form.get("tls_cert", DEFAULTS["tls_cert"]).strip() or DEFAULTS["tls_cert"],
        "tls_key": request.form.get("tls_key", DEFAULTS["tls_key"]).strip() or DEFAULTS["tls_key"],
    }
    try:
        if form["ws_enabled"]: form["ws_port"] = _coerce_int(request.form.get("ws_port", ""), "WS port")
        else: form["ws_port"] = DEFAULTS["ws_port"]
        if form["tls_enabled"]: form["tls_port"] = _coerce_int(request.form.get("tls_port", ""), "TLS port")
        else: form["tls_port"] = DEFAULTS["tls_port"]
    except ValueError as exc:
        return redirect(url_for("index", error=str(exc)))

    if not form["ws_enabled"] and not form["tls_enabled"]:
        return redirect(url_for("index", error="Enable at least one inbound."))

    existing = _find_config(store, form["id"])
    if existing:
        form["enabled"] = existing.get("enabled", True)
        existing.update(form)
    else:
        form["enabled"] = True
        store.setdefault("configs", []).append(form)

    ensure_dirs()
    ensure_certs(form["domain"])
    write_config(build_config(store.get("configs", [])))
    _save_store(store)
    start_xray()
    return redirect(url_for("index", message="Config saved and Xray restarted."))
''', text, flags=re.DOTALL, count=1
)

text = re.sub(
    r'@app\.route\("/activate/<config_id>", methods=\["POST"\]\)\ndef activate\(config_id: str\):.*?(?=@app\.route\("/restart", methods=\["POST"\]\))',
    '''@app.route("/toggle/<config_id>", methods=["POST"])
def toggle(config_id: str):
    store = _load_store()
    item = _find_config(store, config_id)
    if not item:
        return redirect(url_for("index", error="Config not found."))
    ensure_dirs()
    ensure_certs(item["domain"])
    item["enabled"] = not item.get("enabled", True)
    write_config(build_config(store.get("configs", [])))
    _save_store(store)
    start_xray()
    return redirect(url_for("index", message=f"Config {'enabled' if item['enabled'] else 'disabled'}."))
''',
    text, flags=re.DOTALL, count=1
)

text = re.sub(
    r'def bootstrap\(\) -> None:.*?start_xray\(\)',
    '''def bootstrap() -> None:
    from uuid import uuid4
    ensure_dirs()
    store = _load_store()
    if not store.get("configs"):
        default_item = dict(DEFAULTS)
        default_item["id"] = str(uuid4())
        default_item["enabled"] = True
        store["configs"] = [default_item]
        _save_store(store)
        
    if not CONFIG_PATH.exists():
        for c in store.get("configs", []):
            ensure_certs(c["domain"])
        write_config(build_config(store.get("configs", [])))
    start_xray()''',
    text, flags=re.DOTALL, count=1
)

with open('web/app.py', 'w') as f:
    f.write(text)
print("Updated app.py successfully")
