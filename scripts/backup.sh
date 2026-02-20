#!/bin/bash

# 💾 Backup Xray Configuration
# Creates timestamped backup

BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="xray_backup_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "Creating backup: $BACKUP_NAME"

tar -czf "$BACKUP_DIR/$BACKUP_NAME" \
    xray-configs/ \
    certs/ \
    .env \
    docker-compose.yml \
    Dockerfile \
    2>/dev/null

SIZE=$(du -h "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)
echo "✅ Backup created: $BACKUP_DIR/$BACKUP_NAME ($SIZE)"
