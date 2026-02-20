#!/bin/bash

# 📊 Real-time Xray Server Monitor
# Displays live container stats and logs

INTERVAL=5

while true; do
    clear
    echo "========================================="
    echo "Xray Server Monitor - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================="
    echo ""

    echo "📊 Container Status:"
    docker-compose ps xray-server
    echo ""

    echo "💾 Resource Usage:"
    docker stats --no-stream xray-server --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "Container not running"
    echo ""

    echo "🌐 Active Connections:"
    docker exec xray-server netstat -an 2>/dev/null | grep ESTABLISHED | wc -l || echo "0"
    echo ""

    echo "📋 Recent Logs (last 10 lines):"
    docker-compose logs --tail=10 xray-server 2>/dev/null | tail -10
    echo ""

    echo "Press Ctrl+C to exit. Refreshing in ${INTERVAL}s..."
    sleep $INTERVAL
done
