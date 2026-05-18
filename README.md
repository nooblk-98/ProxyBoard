<picture>
  <source media="(prefers-color-scheme: dark)" srcset="web/static/icon-light.svg">
  <source media="(prefers-color-scheme: light)" srcset="web/static/icon-dark.svg">
  <img alt="ProxyBoard" src="web/static/icon-light.svg" width="120">
</picture>

# ProxyBoard — Xray Dashboard

> A modern web UI for managing [Xray-core](https://github.com/XTLS/Xray-core) VPN/proxy configurations with real-time monitoring, live traffic stats, log streaming, and one-command Docker deployment.

[![Docker Image](https://img.shields.io/docker/v/lahiruh98s/proxyboard?logo=docker)](https://hub.docker.com/r/lahiru98s/proxyboard)
[![Docker Pulls](https://img.shields.io/docker/pulls/lahiru98s/proxyboard)](https://hub.docker.com/r/lahiru98s/proxyboard)
[![ platforms](https://img.shields.io/badge/linux-amd64%20%7C%20arm64-blue)](#)

---

## Quick Start

```bash
docker run -d \
  --name proxyboard \
  --restart unless-stopped \
  --network host \
  -v proxyboard-data:/data \
  -e XRAY_DOMAIN=yourdomain.com \
  lahiru98s/proxyboard:latest
```

Open the UI at `http://your-server-ip:8088`.

> **Note:** Using `--network host` is recommended so Xray can bind to any port. If you prefer bridge networking, publish ports explicitly.

---

## Screenshots

| Dashboard | Configurations |
|---|---|
| ![Dashboard](images/dash.png) | ![Configs](images/configs.png) |

---

## Features

- **Dashboard** — Live CPU, memory, disk, and network gauges with traffic history chart
- **Configurations** — Create, edit, enable/disable multiple Xray inbounds (VLESS/VMESS over WS and WS+TLS)
- **QR Code Sharing** — One-click QR code generation and copy-to-clipboard for client import URLs
- **Live Log Viewer** — SSE-powered real-time tailing of Xray access and error logs
- **Backup & Restore** — Export/import all configurations as a single JSON file
- **Config Validation** — Run Xray's built-in `--test` against the active config
- **Version Switcher** — Switch Xray core versions on the fly with live download progress
- **Auto-Restart Watchdog** — Automatically restarts Xray if the process crashes
- **Auth Protection** — Optional username/password or SHA-256 hashed password login
- **Light/Dark Theme** — Toggle from the Settings panel
- **Docker Healthcheck** — `/healthz` endpoint wired to Docker `HEALTHCHECK`
- **Multi-Arch Images** — Published for both `linux/amd64` and `linux/arm64`

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `XRAY_DOMAIN` | `example.com` | Domain / SNI for Xray client configs |
| `UI_PORT` | `8088` | Web UI listening port |
| `UI_USERNAME` | `admin` | Login username (ignored if `UI_PASSWORD` not set) |
| `UI_PASSWORD` | — | Enables password-based auth when set |
| `UI_PASSWORD_HASH` | — | SHA-256 hex digest of password (alternative to plain text) |
| `XRAY_VERSIONS_CONFIG` | `/opt/xray/versions.json` | Path to the Xray versions manifest |
| `XRAY_STABLE_VERSIONS` | — | Comma-separated override for the version list |

---

## Data & Certificates

All runtime data lives under `/data` (persisted via the `proxyboard-data` volume):

```
/data/
  config.json        # Active Xray configuration
  configs.json       # UI-managed config store
  certs/             # Auto-generated self-signed TLS certificates
  logs/              # Xray access & error logs
  xray.pid           # Xray process PID
```

Self-signed certificates are generated automatically on first boot. Replace `/data/certs/cert.pem` and `/data/certs/key.pem` with your own for production use.

---

## Docker Compose

```yaml
services:
  proxyboard:
    image: lahiru98s/proxyboard:latest
    container_name: proxyboard
    restart: unless-stopped
    network_mode: host
    environment:
      - XRAY_DOMAIN=yourdomain.com
      - UI_PORT=8088
    volumes:
      - proxyboard-data:/data

volumes:
  proxyboard-data:
```

To update:

```bash
docker compose pull && docker compose up -d
```

---

## Ports

| Port | Purpose |
|---|---|
| `8088` | Web management UI |
| Per-config | Xray proxy inbounds (WS / WS+TLS) |

---

## Built With

- **Backend:** Python 3.12 + Flask
- **Frontend:** Vanilla JS, CSS, HTML (server-rendered)
- **Proxy Core:** [Xray-core](https://github.com/XTLS/Xray-core)
- **Container:** Docker multi-stage build on `python:3.12-slim`

---

## Developed by [nooblk](https://github.com/nooblk-98)
