FROM ubuntu:22.04

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    certbot \
    openssl \
    systemctl \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Xray-core
RUN bash <(curl -Ls https://raw.githubusercontent.com/XTLS/Xray-install/main/install-release.sh)

# Create directories for configurations and certificates
RUN mkdir -p /etc/xray /certs /var/log/xray

# Copy Xray configuration files
COPY xray-configs/ /etc/xray/

# Create certificate directory
RUN mkdir -p /certs && mkdir -p /tmp/certs_temp

# Try to copy certificates if they exist
COPY certs/* /tmp/certs_temp/ 2>/dev/null || true
RUN if [ "$(ls -A /tmp/certs_temp/)" ]; then mv /tmp/certs_temp/* /certs/; fi && rm -rf /tmp/certs_temp

# Expose ports
EXPOSE 80 443 8080 8443

# Set proper permissions
RUN chmod 644 /etc/xray/*.json

# Start Xray
CMD ["xray", "-c", "/etc/xray/config.json"]
