# Xray Server Web UI

Run Xray with a built-in web UI that edits `config.json`, restarts the server, and shows status.

## Quick start

```bash
docker compose up -d --build
```

Open the UI at:

- `http://localhost:8088`

## What you get

- Web UI to edit the full Xray JSON config
- Status page showing running state and last config update
- Self-signed TLS certs generated on first run in `/data/certs`

## Data persistence

A Docker volume named `xray-data` stores:

- `/data/config.json`
- `/data/certs/`
- `/data/logs/`

## Optional environment variables

You can set these in `docker-compose.yml` if desired:

- `XRAY_DOMAIN` (default: `example.com`)
- `UI_PORT` (default: `8088`)

## Notes

- Ports `80`, `443`, `8080`, `8443` are mapped by default. Adjust `docker-compose.yml` if you need different ports.
- Replace the self-signed certs in `/data/certs` for production use.