#!/bin/bash
set -e

# Start HTTP server
gunicorn \
  --bind 0.0.0.0:${UI_PORT:-8088} \
  --workers 2 \
  --timeout 30 \
  /opt/xray-web/app:app &

HTTP_PID=$!

# Start HTTPS server if certs exist
if [ -f /data/certs/cert.pem ] && [ -f /data/certs/key.pem ]; then
  gunicorn \
    --bind 0.0.0.0:$((${UI_PORT:-8088} + 1)) \
    --certfile=/data/certs/cert.pem \
    --keyfile=/data/certs/key.pem \
    --workers 2 \
    --timeout 30 \
    /opt/xray-web/app:app &
  
  HTTPS_PID=$!
fi

# Wait for processes
wait