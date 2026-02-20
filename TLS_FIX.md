# TLS Connection Fix Guide

## Problem
TLS handshake error: "no cipher suite supported by both client and server"

## Root Causes
1. **Self-signed certificate** - Client doesn't trust the certificate
2. **Restrictive cipher suites** - Server only supported TLS 1.3 suites
3. **Client configuration** - May need allowInsecure=true for self-signed certs

## Solution Applied

### 1. Updated Xray TLS Configuration
Added comprehensive cipher suite support for both TLS 1.2 and 1.3:
- TLS 1.2 suites: `ECDHE_ECDSA/RSA_WITH_AES_*_GCM_SHA*`
- TLS 1.2 suites: `ECDHE_ECDSA/RSA_WITH_CHACHA20_POLY1305`
- TLS 1.3 suites: `TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256`, `TLS_AES_128_GCM_SHA256`
- Added ALPN support: `http/1.1`

### 2. Restart Xray Server
```bash
cd ~/xray-server
docker compose restart
```

### 3. Verify Configuration
```bash
# Check container is running
docker ps | grep xray

# View logs
docker logs xray-server-xray-server-1 --tail=50

# Test port 443
openssl s_client -connect vx-ui.duckdns.org:443 -servername vx-ui.duckdns.org
```

## Client Configuration Fix

### For V2RayN/V2RayNG (Recommended)

**Port 443 (TLS+WebSocket):**
```
Protocol: VLESS
Address: vx-ui.duckdns.org
Port: 443
UUID: [your-uuid-from-install]
Flow: (leave empty)
Encryption: none
Network: ws
Path: /ws443
Host: vx-ui.duckdns.org
TLS: tls
SNI: vx-ui.duckdns.org
ALPN: http/1.1
AllowInsecure: true    ← CRITICAL for self-signed certs!
```

**Port 8443 (TLS+WebSocket):**
```
Protocol: VLESS
Address: vx-ui.duckdns.org
Port: 8443
UUID: [your-uuid-from-install]
Flow: (leave empty)
Encryption: none
Network: ws
Path: /ws8443
Host: vx-ui.duckdns.org
TLS: tls
SNI: vx-ui.duckdns.org
ALPN: http/1.1
AllowInsecure: true    ← CRITICAL for self-signed certs!
```

### For Non-TLS Ports (If TLS still fails)

**Port 80 (HTTP WebSocket):**
```
Protocol: VLESS
Address: vx-ui.duckdns.org
Port: 80
UUID: [your-uuid-from-install]
Encryption: none
Network: ws
Path: /ws
Host: vx-ui.duckdns.org
TLS: none    ← No TLS, should work immediately
```

## Testing Steps

1. **Restart Docker container:**
   ```bash
   cd ~/xray-server
   docker compose down
   docker compose up -d
   ```

2. **Check if server is listening:**
   ```bash
   netstat -tlnp | grep -E '443|8443|80|8080'
   ```

3. **Test TLS handshake:**
   ```bash
   # Should show cipher suite agreement
   openssl s_client -connect vx-ui.duckdns.org:443 -servername vx-ui.duckdns.org 2>&1 | grep -E 'Cipher|Protocol'
   ```

4. **Connect with client:**
   - Start with port 80 (no TLS) to verify basic connectivity
   - If port 80 works, move to port 443 with `allowInsecure: true`

## Expected Output After Fix

### Successful TLS Handshake:
```
SSL handshake has read 1234 bytes and written 567 bytes
---
Protocol  : TLSv1.3
Cipher    : TLS_AES_256_GCM_SHA384
```

### Successful Connection in Client:
- Ping should show <100ms
- Connection status: Connected
- Traffic should flow (test with browser)

## If Still Failing

### Option 1: Get Real Certificate (Recommended)
```bash
cd ~/xray-server
# Update .env file
nano .env

# Change:
# USE_SELF_SIGNED_CERT=true
# To:
USE_SELF_SIGNED_CERT=false
LETSENCRYPT_EMAIL=your-real-email@example.com

# Re-run certificate setup
./scripts/setup-certs.sh

# Restart
docker compose restart
```

### Option 2: Use Non-TLS Ports
Ports 80 and 8080 don't use TLS and should work without certificate issues:
- Port 80: `/ws`
- Port 8080: `/ws8080`

### Option 3: Debug TLS Issue
```bash
# Check certificate validity
openssl x509 -in certs/cert.pem -text -noout | grep -E 'Subject:|Issuer:|Not'

# Test cipher suite negotiation
openssl s_client -cipher 'ECDHE-RSA-AES256-GCM-SHA384' -connect vx-ui.duckdns.org:443

# Check Xray logs for specific errors
docker logs xray-server-xray-server-1 2>&1 | grep -i "tls\|handshake\|cipher"
```

## Quick Recovery Commands

```bash
# Full restart
cd ~/xray-server
docker compose down
docker compose up -d

# View real-time logs
docker logs -f xray-server-xray-server-1

# Check listening ports
ss -tlnp | grep -E '443|8443'

# Test local connection
curl -v -k https://localhost:443

# Rebuild if config changed
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Summary
The TLS configuration has been updated with comprehensive cipher suite support. You need to:
1. ✅ Restart Docker container
2. ✅ Set `allowInsecure: true` in client for self-signed cert
3. ✅ Test connection starting with port 80, then 443

If issues persist, consider getting a real Let's Encrypt certificate by setting `USE_SELF_SIGNED_CERT=false` in .env.
