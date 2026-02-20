#!/bin/bash

# 🔐 Setup SSL Certificates for Xray
# Obtains Let's Encrypt or generates self-signed certificates

set -e

DOMAIN="${1:-example.com}"
EMAIL="${2:-admin@example.com}"
CERT_DIR="./certs"

echo "========================================="
echo "SSL Certificate Setup"
echo "========================================="
echo ""

if [ "$DOMAIN" = "example.com" ]; then
    echo "Usage: bash scripts/setup-certs.sh your_domain.com admin@example.com"
    exit 1
fi

mkdir -p "$CERT_DIR"

echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
fi

echo "Obtaining SSL certificate from Let's Encrypt..."
echo ""

# Request certificate
sudo certbot certonly \
    --standalone \
    --agree-tos \
    --no-eff-email \
    -m "$EMAIL" \
    -d "$DOMAIN" \
    --force-renewal

# Copy certificates
LETSENCRYPT_PATH="/etc/letsencrypt/live/$DOMAIN"

if [ -d "$LETSENCRYPT_PATH" ]; then
    sudo cp "$LETSENCRYPT_PATH/fullchain.pem" "$CERT_DIR/cert.pem"
    sudo cp "$LETSENCRYPT_PATH/privkey.pem" "$CERT_DIR/key.pem"
    
    sudo chown $(whoami):$(whoami) "$CERT_DIR/cert.pem" "$CERT_DIR/key.pem"
    chmod 644 "$CERT_DIR/cert.pem"
    chmod 600 "$CERT_DIR/key.pem"
    
    echo ""
    echo "✅ Certificates obtained successfully!"
    echo "   Cert: $CERT_DIR/cert.pem"
    echo "   Key: $CERT_DIR/key.pem"
else
    echo "❌ ERROR: Certificate path not found"
    exit 1
fi
