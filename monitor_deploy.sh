#!/bin/bash
# Monitor de despliegue: consulta /ping cada segundo y registra hora, versión y código HTTP.
# Uso: ./monitor_deploy.sh <url-del-ambiente>
URL="${1:?Uso: ./monitor_deploy.sh <url-del-ambiente>}"
while true; do
  RESP=$(curl -s -m 3 -w " | HTTP %{http_code}" "$URL/ping")
  echo "$(date +%H:%M:%S) | $RESP"
  sleep 1
done
