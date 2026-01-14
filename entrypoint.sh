#!/bin/bash
set -e

# Default VNC password if not set
export VNC_PASSWORD=${VNC_PASSWORD:-coomerdl}
export RESOLUTION=${RESOLUTION:-1280x800x24}
export PORT=${PORT:-8080}

echo "Starting CoomerDL Cloud Container..."
echo "Resolution: $RESOLUTION"
echo "Port: $PORT"
echo "VNC Password set."

# Ensure .Xauthority permissions (if needed in some environments)
# touch ~/.Xauthority

# Start Supervisor
# Supervisor will handle Xvfb, Fluxbox, VNC, and the App
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
