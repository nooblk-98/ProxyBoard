# NoobX-UI - Xray Dashboard

A modern web UI for managing Xray VPN configurations with real-time status monitoring and easy configuration management.

## Quick start

1. Edit `docker-compose.yml` and set your domain:
```yaml
environment:
  - UI_PORT=8088
  - XRAY_DOMAIN=yourdomain.com
```

2. Start the server:
```bash
docker compose up -d --build
```

Open the UI at:

- `http://localhost:8088`

## Features

- **Dashboard** - Real-time monitoring of Xray engine status, CPU usage, memory, and transfer speeds
- **Configurations** - Create, edit, enable/disable multiple Xray inbound configurations
- **Web UI** - Clean Material Design interface with dark mode
- **Port Management** - Prevent port conflicts between configurations
- **Self-signed TLS** - Automatic certificate generation
- **Docker Ready** - One-command deployment with Docker Compose

## Screenshots

### Dashboard
View real-time status, connection info, and system metrics.

![Dashboard](./images/dash.png)

### Configurations
Manage multiple Xray configurations easily.

![Configurations](./images/configs.png)

## What you get

- Modern web UI to manage Xray configurations
- Status page showing running state and active connections
- Real-time system monitoring (CPU, memory, traffic)
- Self-signed TLS certs generated on first run in `/data/certs`
- Port conflict detection between configs

## Data persistence

A Docker volume named `xray-data` stores:

- `/data/config.json` - Main Xray configuration
- `/data/configs.json` - Multiple config profiles
- `/data/certs/` - SSL certificates
- `/data/logs/` - Xray access and error logs

## Configuration

Edit these in `docker-compose.yml` under `environment`:

- `XRAY_DOMAIN` - Your domain name (default: `example.com`)
- `UI_PORT` - Web UI port (default: `8088`)

## Notes

- Port `8088` is exposed for the web UI
- Xray inbound ports (80, 443, 8080, 8443) can be configured per configuration
- Replace the self-signed certs in `/data/certs` for production use
- Developed by [nooblk](https://github.com/nooblk-98)