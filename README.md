<picture>
  <source media="(prefers-color-scheme: dark)" srcset="web/static/icon-light.svg">
  <source media="(prefers-color-scheme: light)" srcset="web/static/icon-dark.svg">
  <img alt="ProxyBoard" src="web/static/icon-light.svg" width="120">
</picture>

# ProxyBoard — Xray Dashboard

> A modern, self-hosted web dashboard for managing [Xray-core](https://github.com/XTLS/Xray-core) VPN/proxy configurations. Monitor real-time system metrics, manage proxy inbounds, stream live logs, switch Xray core versions on the fly, and deploy anywhere with a single Docker command.

[![Docker Image](https://img.shields.io/docker/v/lahiru98s/proxyboard?logo=docker)](https://hub.docker.com/r/lahiru98s/proxyboard)
[![Docker Pulls](https://img.shields.io/docker/pulls/lahiru98s/proxyboard)](https://hub.docker.com/r/lahiru98s/proxyboard)
[![Platforms](https://img.shields.io/badge/linux-amd64%20%7C%20arm64-blue)](#)
[![License](https://img.shields.io/badge/license-MIT-green)](#license)

---

## Table of Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Features](#features)
- [Quick Start](#quick-start)
- [Docker Compose](#docker-compose)
- [Building from Source](#building-from-source)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Data Directory](#data-directory)
  - [Ports Reference](#ports-reference)
- [Usage Guide](#usage-guide)
  - [Dashboard](#dashboard)
  - [Managing Configurations](#managing-configurations)
  - [Log Viewer](#log-viewer)
  - [Version Management](#version-management)
  - [Backup & Restore](#backup--restore)
  - [TLS Certificates](#tls-certificates)
- [API Reference](#api-reference)
- [Development](#development)
  - [Prerequisites](#prerequisites)
  - [Local Setup](#local-setup)
  - [Running Tests](#running-tests)
  - [Linting & Type Checking](#linting--type-checking)
- [CI/CD](#cicd)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

ProxyBoard is a lightweight, self-hosted web interface for [Xray-core](https://github.com/XTLS/Xray-core) — the popular proxy platform that powers VLESS, VMESS, and other modern proxy protocols. The application is designed for server administrators who need a convenient way to manage multiple proxy inbounds, monitor server health, and maintain their Xray deployment without touching configuration files or the command line.

**Key design principles:**

- **Single-binary deployment** — everything runs in a single Docker container
- **File-based storage** — no external database required; all state is kept in JSON files on a persistent volume
- **Real-time by default** — live metrics, live log streaming via SSE, instant config reload
- **Self-contained** — Xray-core binaries are downloaded and managed from the UI itself; no manual installation needed

---

## Screenshots

| Dashboard | Configurations |
|---|---|
| ![Dashboard](images/dash.png) | ![Configs](images/configs.png) |

> *Note: The dashboard shows live system gauges (CPU, memory, disk, network) and per-config traffic statistics. The configurations panel provides full CRUD for Xray inbounds with QR code sharing.*

---

## Features

### Dashboard & System Monitoring
- **Real-time system metrics** — CPU load, memory usage, disk utilization, and server uptime via `/proc`
- **Live network speed gauges** — upload/download throughput with auto-scaling units
- **Traffic history chart** — 30-second rolling window of network activity rendered with Chart.js
- **Per-config traffic stats** — per-user uplink/downlink data pulled from Xray's gRPC StatsService API
- **Configurable auto-refresh** — polling intervals of 3, 5, or 10 seconds
- **Xray engine status** — process health, PID, version, and configuration last-modified timestamp

### Configuration Management
- **Full CRUD** — create, read, update, and delete Xray proxy inbounds through a web form
- **Dual inbound support** — each config can expose both WebSocket (WS) and WebSocket + TLS (WSS) inbounds
- **Protocol support** — VLESS and VMESS protocols with automatically generated UUIDs
- **Port collision detection** — duplicate ports across configs are rejected with a clear error
- **Enable/disable toggle** — quickly disable an inbound without deleting it; disabled configs are excluded from the generated Xray configuration
- **Delete guard** — at least one config must always exist; deletion of the last config is refused
- **Auto-generated Xray config** — the application builds a complete `config.json` with inbounds, outbounds, routing rules, DNS, and StatsService policy

### QR Code & Client Sharing
- **One-click share links** — generates VLESS URI or VMESS base64-encoded links for each inbound
- **QR code generation** — scannable PNG QR codes for importing into client apps (e.g., v2rayNG, Nekoray)
- **Copy to clipboard** — quick-copy buttons for share URLs

### Live Log Viewer
- **SSE-powered streaming** — Server-Sent Events for real-time log tailing
- **Dual log streams** — separate tabs for Xray access log and error log
- **Initial tail buffer** — last 100 lines loaded on page connect
- **Color-coded output** — error and warning lines highlighted for quick scanning
- **Toggle streaming** — start/stop log listening without reloading the page

### Xray Core Management
- **Version download & switching** — choose from 27+ Xray-core versions in the UI; downloads with live progress
- **Multi-architecture** — supports amd64, arm64, and arm32 binaries
- **Automatic installation** — binaries are downloaded from GitHub releases, extracted, and symlinked
- **Start/stop/restart** — full lifecycle management from the web UI
- **Crash watchdog** — background thread checks every 10 seconds and restarts Xray if the process dies

### Backup & Restore
- **JSON export** — download all configurations as a single portable JSON file
- **Full import** — upload a backup file to replace all configs atomically
- **Cross-instance migration** — backup from one server and restore on another

### Security & Authentication
- **Optional password auth** — enable by setting `UI_PASSWORD` or `UI_PASSWORD_HASH`
- **SHA-256 hashed passwords** — no plain-text secrets in environment if using the hash option
- **Session-based login** — Flask sessions with configurable secret key
- **Docker healthcheck** — built-in `/healthz` endpoint wired to Docker `HEALTHCHECK`

### TLS Certificate Management
- **Auto-generated self-signed certs** — created on first boot via OpenSSL
- **Manual upload** — copy existing PEM certificate and key files into the data directory
- **Certificate regeneration** — one-click regeneration from the settings panel

### UI/UX
- **Light/Dark theme** — toggleable with localStorage persistence
- **Responsive design** — desktop sidebar layout collapses to a mobile bottom tab bar at 768px
- **Reduce motion** — accessibility setting to disable gauge animations
- **Material-inspired CSS** — custom design system with CSS custom properties

---

## Quick Start

The fastest way to get ProxyBoard running:

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

> **Important:** Using `--network host` is recommended because Xray needs to bind to arbitrary ports for proxy inbounds. If you prefer bridge networking, publish all required ports explicitly with `-p` flags.

### Default Login

| Setting | Default |
|---|---|
| Username | `admin` |
| Password | *(none — auth is disabled by default)* |
| Port | `8088` |

Authentication is **disabled by default**. To enable it, pass `-e UI_PASSWORD=your-secure-password`.

---

## Docker Compose

### Using the Prebuilt Image

```yaml
# docker-compose.yml
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

```bash
docker compose up -d
```

### Building from Source

```yaml
# docker-compose.yml
services:
  xray-web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: xray-web
    restart: unless-stopped
    network_mode: host
    environment:
      - UI_PORT=8088
      - XRAY_DOMAIN=vpn.example.com
    volumes:
      - xray-data:/data
    cap_add:
      - NET_BIND_SERVICE

volumes:
  xray-data:
```

```bash
docker compose up -d --build
```

### Updating

```bash
docker compose pull && docker compose up -d
```

---

## Building from Source

### Prerequisites

- Linux server (or VM) with Docker installed
- A domain name pointing to your server (for TLS configs)
- Ports 80, 443 (or your chosen proxy ports) accessible from clients

### Clone & Build

```bash
git clone https://github.com/nooblk-98/noobx-ui.git
cd noobx-ui
docker compose up -d --build
```

### Manual Build

```bash
docker build -t proxyboard:latest .
docker run -d \
  --name proxyboard \
  --restart unless-stopped \
  --network host \
  -v proxyboard-data:/data \
  -e XRAY_DOMAIN=yourdomain.com \
  proxyboard:latest
```

---

## Configuration

### Environment Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `XRAY_DOMAIN` | `example.com` | Yes | Domain / SNI used when generating client share links and Xray TLS configs |
| `UI_PORT` | `8088` | No | Port the web management UI listens on |
| `UI_USERNAME` | `admin` | No | Login username (only used when `UI_PASSWORD` or `UI_PASSWORD_HASH` is set) |
| `UI_PASSWORD` | *(unset)* | No | Enables password-based authentication when set. Use a strong password. |
| `UI_PASSWORD_HASH` | *(unset)* | No | SHA-256 hex digest of the password. Alternative to `UI_PASSWORD` for avoiding plain-text secrets. |
| `UI_SECRET_KEY` | *(auto-generated)* | No | Flask session signing key. Set to a random value in production. |
| `XRAY_DATA_DIR` | `/data` | No | Root directory for all runtime data (configs, certs, logs, PID) |
| `XRAY_BIN` | `/usr/local/bin/xray` | No | Path to the Xray binary symlink |
| `XRAY_VERSIONS_DIR` | `/data/xray/versions` | No | Directory that stores downloaded Xray core version binaries |
| `XRAY_VERSIONS_CONFIG` | `/opt/xray/versions.json` | No | Path to the Xray versions manifest file |
| `XRAY_STABLE_VERSIONS` | *(unset)* | No | Comma-separated override for the version list (e.g., `v26.2.6,v26.1.23`) |

### Data Directory

All runtime state is persisted to a Docker volume mounted at `/data`. The directory structure is:

```
/data/
├── config.json          # Active Xray configuration (auto-generated)
├── configs.json         # UI-managed proxy inbound configurations
├── certs/
│   ├── cert.pem         # TLS certificate (auto-generated or uploaded)
│   └── key.pem          # TLS private key
├── logs/
│   ├── access.log       # Xray access log
│   └── error.log        # Xray error log
├── xray.pid             # Xray process PID file
├── xray.version         # Currently installed Xray core version key
└── xray/
    └── versions/        # Downloaded Xray core version binaries
        ├── v26.2.6/
        │   ├── xray
        │   ├── geosite.dat
        │   └── geoip.dat
        ├── v26.2.4/
        └── ...
```

> **Production note:** Replace the auto-generated self-signed certificates in `/data/certs/` with certificates from a trusted CA for production deployments.

### Ports Reference

| Port | Purpose |
|---|---|
| `8088` | ProxyBoard web management UI |
| `10085` | Xray gRPC API (internal — stats queries). Bound to `127.0.0.1` only. |
| Per-config | Xray proxy inbounds — each config defines its own WS and/or WSS ports |

---

## Usage Guide

### Dashboard

The dashboard provides a real-time overview of your server and Xray instance:

- **System Gauges** — canvas-based animated gauges showing CPU load, memory usage, and disk utilization
- **Network Speed** — upload/download throughput with auto-scaling (B/s, KB/s, MB/s)
- **Traffic Chart** — 30-second rolling line chart of network activity
- **Engine Status** — Xray process health (running/stopped), PID, version, and config last-modified time
- **Config Traffic Table** — per-config uplink and downlink statistics from Xray's API
- **Quick Actions** — restart Xray, copy share links, generate QR codes

The dashboard auto-refreshes at the interval configured in Settings (default: 3 seconds).

### Managing Configurations

Navigate to the **Configurations** page to manage proxy inbounds.

**Creating a config:**

1. Click **Add Configuration**
2. Choose a protocol: **VLESS** or **VMESS**
3. Select the network security type:
   - **WebSocket (No TLS)** — for plain WS connections
   - **WebSocket + TLS** — for secure WSS connections with TLS encryption
   - You can enable **both** on a single config for dual inbound support
4. Fill in the port, path, UUID (auto-generated if left blank), and domain
5. Click **Save**

**Additional operations:**

| Action | Description |
|---|---|
| **Edit** | Click the edit icon on any config row to modify its parameters |
| **Toggle** | Use the switch to enable/disable a config without deleting it |
| **Delete** | Remove a config entirely (at least one config must remain) |
| **Share** | Click the QR icon to view share links and scannable QR codes |
| **Copy** | Click the copy button to copy a share URL to your clipboard |

### Log Viewer

The **Logs** page provides real-time access to Xray's logging output:

- **Access Log** — live stream of all proxy connections and traffic
- **Error Log** — live stream of Xray errors and warnings
- **Toggle streaming** — start/stop the SSE connection with a single button
- **Auto-scroll** — logs auto-scroll to the bottom; pause by scrolling up
- **Color highlighting** — error lines in red, warnings in yellow for quick visual scanning

### Version Management

From the **Settings** page, you can manage Xray core versions:

1. The version selector shows all available versions from the manifest
2. Installed versions are marked with a badge
3. Select a version and click **Switch**:
   - If already installed, Xray is restarted with the selected version immediately
   - If not installed, a download progress modal shows the download status (percentage, speed)
   - After download completes, Xray is automatically switched to the new version

### Backup & Restore

- **Export** — click **Download Backup** on the Settings page to save all configs as JSON
- **Import** — upload a previously exported JSON file; all current configs are replaced

### TLS Certificates

- **Self-signed** — click **Generate Self-Signed Certificate** to create a new cert/key pair for the current domain
- **Manual** — specify paths to existing PEM certificate and key files on the server filesystem; they are copied into the data directory

---

## API Reference

ProxyBoard exposes several API endpoints for integration and monitoring.

### Public Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/healthz` | No | Health check — returns `200` if Xray is running, `503` if stopped |
| `GET` | `/status` | No | Full system and Xray status as JSON |

### Authenticated Endpoints

All endpoints below require authentication when `UI_PASSWORD` is set.

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Redirects to `/dashboard` |
| `GET` | `/dashboard` | Dashboard page |
| `GET` | `/configurations` | Configurations management page |
| `GET` | `/settings` | Settings page |
| `GET` | `/logs` | Log viewer page |
| `POST` | `/save` | Create or update a proxy configuration |
| `POST` | `/delete/<config_id>` | Delete a configuration |
| `POST` | `/toggle/<config_id>` | Enable or disable a configuration |
| `POST` | `/restart` | Restart the Xray process |
| `POST` | `/xray/switch` | Switch Xray core version |
| `GET` | `/xray/install-stream/<version_key>` | SSE stream for Xray download progress |
| `GET` | `/logs/stream/<access\|error>` | SSE stream for live log tailing |
| `GET` | `/backup/export` | Download all configs as JSON |
| `POST` | `/backup/import` | Upload and restore configs from JSON |
| `POST` | `/cert/self-signed` | Regenerate self-signed TLS certificate |
| `POST` | `/cert/manual` | Upload custom TLS certificate paths |
| `POST` | `/config/validate` | Run Xray `-test` against the generated config |

### `/status` Response Schema

```json
{
  "running": true,
  "pid": 12345,
  "config_exists": true,
  "config_mtime": "2026-05-18 12:00:00 UTC",
  "data_dir": "/data",
  "domain": "example.com",
  "now": "2026-05-18T12:00:05Z",
  "xray_version": "v26.2.6",
  "xray_bin": "/usr/local/bin/xray",
  "sys_info": {
    "cpu": 0.45,
    "mem": { "total": 8388608, "used": 4194304, "percent": 50.0, ... },
    "disk": { ... },
    "uptime": 3600
  },
  "up_speed": "1.2 MB/s",
  "down_speed": "3.4 MB/s",
  "up_raw": 1200000,
  "down_raw": 3400000,
  "active_ports": [80, 443, 8443],
  "xray_stats": {
    "inbounds": [
      {
        "name": "My Config",
        "downlink": 52428800,
        "uplink": 10485760,
        "tag": "inbound-xxx"
      }
    ]
  }
}
```

---

## Development

### Prerequisites

- Python 3.12+
- Linux environment (for `/proc` filesystem access required by system metrics)
- OpenSSL (for certificate generation)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/nooblk-98/noobx-ui.git
cd noobx-ui

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install flask qrcode[pil] pillow

# Set up a local data directory
export XRAY_DATA_DIR=./data
mkdir -p data/certs data/logs

# Generate a self-signed cert for development
openssl req -x509 -nodes -newkey ec \
  -pkeyopt ec_paramgen_curve:prime256v1 \
  -keyout data/certs/key.pem \
  -out data/certs/cert.pem \
  -days 3650 \
  -subj "/CN=localhost"

# Run the application
cd web
python app.py
```

The UI will be available at `http://localhost:8088`.

> **Note:** Xray binary management and the crash watchdog require Xray to be installed. For UI-only development without Xray running, the dashboard will show Xray as stopped but all management features remain functional.

### Running Tests

```bash
# Unit tests
python -m pytest web/tests/ -v

# Integration test (full endpoint exercise)
PYTHONPATH=web python scripts/qa_integration.py

# Run both
python -m pytest web/tests/ -v && PYTHONPATH=web python scripts/qa_integration.py
```

### Linting & Type Checking

```bash
# Install dev dependencies
pip install ruff mypy

# Lint
ruff check web/

# Type check
mypy web/
```

Configuration for both tools is in `pyproject.toml`:
- **Ruff**: Python 3.12, line length 120, rulesets `E,F,W,I,N,UP,S`
- **Mypy**: strict mode enabled

## Project Structure

```
├── web/
│   ├── app.py                     # Application entry point
│   ├── static/
│   │   ├── app.js                 # Frontend JavaScript (734 lines)
│   │   ├── style.css              # Custom CSS design system (2339 lines)
│   │   ├── icon-dark.svg          # Logo for light backgrounds
│   │   └── icon-light.svg         # Logo for dark backgrounds
│   ├── templates/
│   │   ├── index.html             # Main SPA-like page
│   │   ├── login.html             # Login page
│   │   └── partials/              # Jinja2 partials
│   │       ├── head.html
│   │       ├── sidebar.html
│   │       ├── modals.html
│   │       └── footer.html
│   ├── tests/                     # Pytest unit tests
│   │   ├── conftest.py
│   │   ├── test_config_persistence.py
│   │   └── test_xray_config_builder.py
│   └── ui/                        # Backend modules
│       ├── __init__.py
│       ├── auth.py                # Authentication
│       ├── backup.py              # Backup/restore
│       ├── config_persistence.py  # Config CRUD + JSON store
│       ├── constants.py           # Paths, env vars, defaults
│       ├── log_reader.py          # Log tailing + SSE
│       ├── main.py                # App bootstrap
│       ├── routes.py              # All Flask routes
│       ├── stats.py               # System metrics + Xray stats
│       ├── store.py               # Helper utilities
│       ├── system.py              # Certificate management
│       ├── types.py               # Type definitions
│       ├── validator.py           # Xray config validation
│       ├── watchdog.py            # Auto-restart daemon
│       ├── xray_core.py           # Xray download/switch/start/stop
│       └── xray_config_builder.py # Xray JSON config generator
├── scripts/
│   ├── download_xray_versions.py  # Pre-download Xray binaries (Docker build)
│   └── qa_integration.py          # Full integration test
├── images/                        # Screenshots
├── config.default.json            # Default Xray config template
├── xray-versions.json             # Xray core version manifest
├── Dockerfile                     # Multi-platform Docker build
├── docker-compose.yml             # Production compose (build from source)
├── docker-compose-live.yml        # Compose with prebuilt image
├── pyproject.toml                 # Ruff, mypy, pytest config
├── pytest.ini                     # pytest paths
└── .github/workflows/
    ├── docker-publish.yml         # CI: multi-arch Docker build & push
    └── qa.yml                     # CI: unit + integration tests
```

---

## CI/CD

### GitHub Actions

Two workflows are configured:

**QA — Tests & Validation** (`.github/workflows/qa.yml`):
- Triggers on every push and pull request to any branch
- Sets up Python 3.12, installs dependencies, runs unit tests and the integration test

**Build and Push Docker Image** (`.github/workflows/docker-publish.yml`):
- Triggers on published releases and manual workflow dispatch
- Builds multi-architecture images (`linux/amd64` and `linux/arm64`)
- Pushes to both **Docker Hub** (`lahiru98s/noobx-ui`) and **GitHub Container Registry** (`ghcr.io/nooblk-98/noobx-ui`)
- Uses Docker Buildx with GitHub Actions cache for fast rebuilds

### Docker Image Registries

| Registry | Image |
|---|---|
| Docker Hub | `lahiru98s/proxyboard` |
| GitHub Container Registry | `ghcr.io/nooblk-98/noobx-ui` |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | [Python 3.12](https://www.python.org/) + [Flask 3.0.3](https://flask.palletsprojects.com/) |
| **Frontend** | Vanilla JavaScript (ES6), CSS3 with custom properties, Jinja2 templates |
| **Charting** | [Chart.js](https://www.chartjs.org/) (loaded from CDN) |
| **QR Codes** | [qrcode](https://github.com/lincolnloop/python-qrcode) 7.4 + Pillow 10.4 |
| **Proxy Core** | [Xray-core](https://github.com/XTLS/Xray-core) (downloaded and managed dynamically) |
| **Container** | Docker / Docker Compose, single-stage `python:3.12-slim` image |
| **Testing** | pytest (unit + integration) |
| **Linting** | Ruff, mypy (strict mode) |
| **CI/CD** | GitHub Actions (multi-arch Docker publish + automated testing) |

---

## Contributing

Contributions are welcome and appreciated. Here is how you can help:

### Reporting Issues

- Check the [existing issues](https://github.com/nooblk-98/noobx-ui/issues) to avoid duplicates
- Provide a clear, descriptive title and steps to reproduce
- Include relevant logs, screenshots, and environment details (OS, Docker version, browser)

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Ensure all tests pass:
   ```bash
   python -m pytest web/tests/ -v
   PYTHONPATH=web python scripts/qa_integration.py
   ```
5. Run the linter and type checker:
   ```bash
   ruff check web/
   mypy web/
   ```
6. Commit your changes with a descriptive message
7. Push to your fork and open a pull request

### Development Guidelines

- Follow the existing code style (Ruff ruleset: `E,F,W,I,N,UP,S`)
- Maintain strict type annotations (mypy strict mode)
- Add tests for new features and bug fixes
- Keep the Docker image small — avoid adding unnecessary dependencies
- Update documentation (README, inline docstrings) as needed

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 nooblk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Developed by <a href="https://github.com/nooblk-98">nooblk</a>
</p>
