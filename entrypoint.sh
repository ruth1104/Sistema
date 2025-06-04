#!/bin/sh
set -e

STATIC_DIR="/app/app/static"
INITIAL_DIR="/initial_static"

# Ensure static dir exists
mkdir -p "$STATIC_DIR"

# Always overwrite host static with container's static files
# This ensures container version dominates and replaces changed files
echo "[entrypoint] Syncing static files from container to host volume..."
cp -r "$INITIAL_DIR/." "$STATIC_DIR/"

# Fix permissions (adjust user:group if needed)
chown -R nobody:nogroup "$STATIC_DIR" || true

# Execute main process
exec "$@"