#!/bin/bash
# Health check script for Docker container
# Checks if noVNC is accessible on the configured PORT

PORT=${PORT:-8080}
curl -f "http://localhost:${PORT}/vnc.html" || exit 1
