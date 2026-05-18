"""QA integration test — exercises every app endpoint.

Run from repo root: PYTHONPATH=web python scripts/qa_integration.py
"""

import json
import os
import sys

os.environ["XRAY_DATA_DIR"] = "/tmp/qa-data"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web"))

from ui.routes import create_app

app = create_app()
client = app.test_client()

passed = 0
failed = 0


def check(name, ok):
    global passed, failed
    if ok:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}")


r = client.get("/healthz")
check("healthz", r.status_code in (200, 503))

r = client.get("/status")
check("status returns JSON", "running" in r.get_json())

for path, label in [
    ("/", "root"),
    ("/dashboard", "dashboard"),
    ("/configurations", "configurations"),
    ("/settings", "settings"),
    ("/logs", "logs"),
]:
    r = client.get(path, follow_redirects=True)
    check(f"{label} page", r.status_code == 200)

for i, name in enumerate(["Alpha", "Beta", "Gamma"]):
    r = client.post(
        "/save",
        data={
            "edit_id": "new",
            "name": name,
            "domain": f"{name.lower()}.com",
            "network_security": "ws",
            "ws_port": str(38000 + i),
            "ws_path": f"/{name.lower()}",
            "protocol": "vless",
        },
        follow_redirects=True,
    )
    check(f"create {name}", r.status_code == 200)

store = json.loads(open("/tmp/qa-data/configs.json").read())
names = {c["name"] for c in store["configs"]}
check("3 configs in store", len(names & {"Alpha", "Beta", "Gamma"}) == 3)
alpha = next(c for c in store["configs"] if c["name"] == "Alpha")

r = client.post(
    "/save",
    data={
        "edit_id": alpha["id"],
        "name": "Alpha-Updated",
        "domain": "alpha.com",
        "network_security": "ws",
        "ws_port": "38000",
        "ws_path": "/alpha",
        "protocol": "vless",
    },
    follow_redirects=True,
)
check("update name", "saved" in r.data.decode().lower())

store = json.loads(open("/tmp/qa-data/configs.json").read())
check(
    "name persisted",
    next((c for c in store["configs"] if c["id"] == alpha["id"]), {}).get("name")
    == "Alpha-Updated",
)

r = client.post(
    "/save",
    data={
        "edit_id": "new",
        "name": "Collider",
        "domain": "collide.com",
        "network_security": "ws",
        "ws_port": "38000",
        "ws_path": "/collide",
        "protocol": "vless",
    },
    follow_redirects=True,
)
check("port collision", "already used" in r.data.decode().lower())

beta = next(c for c in store["configs"] if c["name"] == "Beta")
r = client.post(f"/toggle/{beta['id']}", follow_redirects=True)
check("toggle disabled", "disabled" in r.data.decode().lower())
store = json.loads(open("/tmp/qa-data/configs.json").read())
check(
    "actually disabled",
    next((c for c in store["configs"] if c["id"] == beta["id"]), {}).get("enabled")
    == False,
)
r = client.post(f"/toggle/{beta['id']}", follow_redirects=True)
check("toggle enabled back", "enabled" in r.data.decode().lower())

r = client.post(f"/delete/{beta['id']}", follow_redirects=True)
check("delete Beta", "deleted" in r.data.decode().lower())

store = json.loads(open("/tmp/qa-data/configs.json").read())
while len(store["configs"]) > 1:
    cid = store["configs"][0]["id"]
    client.post(f"/delete/{cid}", follow_redirects=True)
    store = json.loads(open("/tmp/qa-data/configs.json").read())
r = client.post(
    f"/delete/{store['configs'][0]['id']}", follow_redirects=True
)
check("delete last refused", "cannot delete" in r.data.decode().lower())

xray = json.loads(open("/tmp/qa-data/config.json").read())
check("xray has inbounds", len(xray.get("inbounds", [])) >= 1)
check("xray has api inbound", any(i["tag"] == "api" for i in xray["inbounds"]))

r = client.post("/config/validate")
check("validate", r.status_code == 200 and "ok" in r.get_json())

r = client.post("/restart", follow_redirects=True)
check("restart", r.status_code == 200)

r = client.get("/backup/export")
check("backup export", r.status_code == 200 and r.content_type == "application/json")

backup_data = json.dumps(
    {
        "configs": [
            {
                "id": "zzz",
                "name": "Imported",
                "ws_enabled": True,
                "ws_port": 39000,
                "ws_path": "/imp",
                "ws_uuid": "00000000-0000-0000-0000-000000000000",
                "domain": "imp.com",
                "protocol": "vless",
                "tls_enabled": False,
            }
        ]
    }
)
r = client.post(
    "/backup/import",
    data={"backup_file": (__import__("io").BytesIO(backup_data.encode()), "backup.json")},
    follow_redirects=True,
)
check("backup import", "Imported" in r.data.decode())

r = client.post("/cert/self-signed", follow_redirects=True)
check("self-signed cert", r.status_code == 200)

r = client.post(
    "/cert/manual",
    data={"cert_path": "/nonexistent/cert.pem", "key_path": "/nonexistent/key.pem"},
    follow_redirects=True,
)
check("manual cert error", "not found" in r.data.decode().lower())

r = client.get("/logs/stream/access")
check("log SSE stream", r.status_code == 200 and r.content_type.startswith("text/event-stream"))

total = passed + failed
print()
print(f"Results: {passed}/{total} passed, {failed}/{total} failed")
sys.exit(0 if failed == 0 else 1)
