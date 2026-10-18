#!/bin/bash
# Valida un despliegue en vivo: consulta /ping cada segundo y muestra hora, código HTTP y versión.
# Uso:  ./monitor_deploy.sh http://TU-AMBIENTE.elasticbeanstalk.com
URL="${1:?Pasa la URL del ambiente}"
while true; do
  RESP=$(curl -s -m 3 -w " | HTTP %{http_code}" "$URL/ping")
  echo "$(date +%H:%M:%S) | $RESP"
  sleep 1
done
