Paso a paso para desplegar (resumen):
1) Clona repo en VM
2) Copia .env con keys (usar BINANCE_TESTNET=true primero)
3) docker compose up -d --build
4) validar endpoints /health y UI
5) paper trading 7-14 días
6) crear API keys reales y cambiar BINANCE_TESTNET=false
