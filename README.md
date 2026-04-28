# ProxyBoard — Xray Dashboard

A modern web UI for managing Xray-core VPN configurations with real-time monitoring, live traffic stats, log viewer, and one-command Docker deployment.

---

## Deployment

### Option 1 — Docker Run (single command)

```bash
docker run -d \
  --name proxyboard \
  --restart unless-stopped \
  -p 8088:8088 \
  -v proxyboard-data:/data \
  -e XRAY_DOMAIN=yourdomain.com \
  -e UI_PORT=8088 \
  lahiru98s/proxyboard:latest
```

Open the UI at `http://your-server-ip:8088`

---

### Option 2 — Docker Compose

Create a `docker-compose.yml`:

```yaml
services:
  proxyboard:
    image: lahiru98s/proxyboard:latest
    container_name: proxyboard
    restart: unless-stopped
    ports:
      - "8088:8088"
    volumes:
      - proxyboard-data:/data
    environment:
      - XRAY_DOMAIN=yourdomain.com
      - UI_PORT=8088
      # Optional: enable login protection
      # - UI_USERNAME=admin
      # - UI_PASSWORD=yourpassword

volumes:
  proxyboard-data:
```

Then run:

```bash
docker compose up -d
```

Pull latest image and restart:

```bash
docker compose pull && docker compose up -d
```

---

## Run without Docker

### Prerequisites

- Python 3.10+
- `openssl` installed (for auto-generated certs)
- Linux (Xray binaries are Linux-only)

### 1. Clone and install dependencies

```bash
git clone https://github.com/nooblk-98/NoobX-UI.git
cd NoobX-UI
pip install -r requirements.txt
```

### 2. Download Xray binary

```bash
python3 scripts/download_xray_versions.py --only-default
```

This downloads the default Xray version into `~/.local/share/xray/versions/` (or the path set by `XRAY_VERSIONS_DIR`).

### 3. Set environment variables

```bash
export XRAY_DOMAIN=yourdomain.com
export UI_PORT=8088
export XRAY_DATA_DIR=./data
export XRAY_VERSIONS_DIR=./data/xray/versions
export XRAY_VERSIONS_CONFIG=./xray-versions.json
# Optional auth
# export UI_USERNAME=admin
# export UI_PASSWORD=yourpassword
```

Or copy `.env.example` to `.env` and edit it, then source it:

```bash
cp .env.example .env
# edit .env
set -a && source .env && set +a
```

### 4. Run the app

```bash
python3 app/app.py
```

Open the UI at `http://localhost:8088`

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `XRAY_DOMAIN` | `example.com` | Your domain / SNI for Xray configs |
| `UI_PORT` | `8088` | Web UI port |
| `UI_USERNAME` | `admin` | Login username (auth disabled if `UI_PASSWORD` not set) |
| `UI_PASSWORD` | _(unset)_ | Login password — enables auth when set |
| `UI_PASSWORD_HASH` | _(unset)_ | SHA-256 hash of password (alternative to plain `UI_PASSWORD`) |
| `XRAY_VERSIONS_CONFIG` | `/opt/xray/versions.json` | Path to versions list JSON |
| `XRAY_STABLE_VERSIONS` | _(unset)_ | Comma-separated version list override |

---

## Features

- **Dashboard** — Live CPU, memory, disk, upload/download gauges + traffic history chart
- **Configurations** — Create, edit, enable/disable multiple Xray inbound configs (VLESS/VMESS, WS/TLS)
- **QR Code sharing** — One-click QR and copy for client import URLs
- **Log Viewer** — Live-tail access and error logs with SSE streaming
- **Backup & Restore** — Export/import all configs as JSON
- **Config Validation** — Run Xray's built-in `--test` against active config
- **Version Switcher** — Switch Xray core versions with live download progress bar
- **Auto-restart watchdog** — Automatically restarts Xray if it crashes
- **Auth protection** — Optional username/password login page
- **Light/Dark theme** — Toggle from Settings
- **Docker Healthcheck** — `/healthz` endpoint wired into `HEALTHCHECK`
- **Multi-arch** — `linux/amd64` and `linux/arm64` images

---

## Data & Certificates

All runtime data is stored in `/data` inside the container (mapped to the `proxyboard-data` volume):

```
/data/
  config.json        # Active Xray config
  configs.json       # UI config store
  certs/             # Auto-generated self-signed TLS certs
  logs/              # Xray access and error logs
  xray.pid           # Xray process ID
```

Self-signed certificates are generated automatically on first run. Replace `/data/certs/cert.pem` and `/data/certs/key.pem` with your own for production.

---

## Ports

| Port | Purpose |
|---|---|
| `8088` | Web UI |
| Configured per-inbound | Xray proxy (WS / WS+TLS) |

---

## Developed by [nooblk](https://github.com/nooblk-98)
