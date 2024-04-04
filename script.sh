#!/bin/bash
set -e  # Sair imediatamente se um comando falhar

chmod 777 /dev/mem
chmod 777 /dev/port

# Executar o aplicativo Python
exec python3 /app/aclient.py