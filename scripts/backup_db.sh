#!/usr/bin/env bash
DB_PATH="${1:-./trading.db}"
DEST_DIR="${2:-./backups}"
mkdir -p "$DEST_DIR"
cp "$DB_PATH" "$DEST_DIR/trading.$(date +%F_%H%M%S).db"
echo "Backup done"
