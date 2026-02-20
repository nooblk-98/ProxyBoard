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

# Create directories for logs and certificates
RUN mkdir -p /etc/xray /certs /var/log/xray

# Set proper permissions
RUN chmod 644 /etc/xray/*.json

# Start Xray
CMD ["xray", "-c", "/etc/xray/config.json"]
