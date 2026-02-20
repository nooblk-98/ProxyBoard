#!/bin/bash

# 🔧 Troubleshoot Xray Server
# Diagnoses common issues

echo "========================================="
echo "Xray Server Troubleshooting"
echo "========================================="
echo ""

echo "1️⃣ Docker Status:"
docker-compose ps
echo ""

echo "2️⃣ Container Logs (last 20 lines):"
docker-compose logs --tail=20 xray-server
echo ""

echo "3️⃣ Port Status:"
docker exec xray-server netstat -tlnp 2>/dev/null | grep xray || echo "Xray not listening"
echo ""

echo "4️⃣ Certificate Check:"
if [ -f "certs/cert.pem" ]; then
    echo "✓ Certificate exists"
    openssl x509 -in certs/cert.pem -noout -dates
else
    echo "✗ Certificate not found"
fi
echo ""

echo "5️⃣ Configuration Check:"
if [ -f ".env" ]; then
    echo "✓ .env file exists"
    grep "DOMAIN=" .env
else
    echo "✗ .env file not found"
fi
