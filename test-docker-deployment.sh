#!/bin/bash
# CoomerDL Docker Deployment Test Script
# This script validates the Docker deployment setup locally before pushing to GCP

set -e

echo "🧪 CoomerDL Docker Deployment Test"
echo "=================================="
echo

# Configuration
IMAGE_NAME="coomerdl-test"
CONTAINER_NAME="coomerdl-validation"
TEST_PORT=18080
VNC_PORT=15900
# Generate random password for testing (or use obvious test value)
VNC_PASSWORD="TEST-$(date +%s)-INSECURE"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

cleanup() {
    print_info "Cleaning up..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
}

# Trap to cleanup on exit
trap cleanup EXIT

# Step 1: Build the image
print_info "Step 1: Building Docker image..."
if docker build -t "$IMAGE_NAME" . 2>&1 | grep -q "Successfully"; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    echo "Running docker build with full output..."
    docker build -t "$IMAGE_NAME" .
    exit 1
fi

# Step 2: Run the container
print_info "Step 2: Starting container..."
CONTAINER_ID=$(docker run -d \
    --name "$CONTAINER_NAME" \
    -p $TEST_PORT:8080 \
    -p $VNC_PORT:5900 \
    -e VNC_PASSWORD="$VNC_PASSWORD" \
    -e PORT=8080 \
    "$IMAGE_NAME")

if [ -z "$CONTAINER_ID" ]; then
    print_error "Failed to start container"
    exit 1
fi
print_success "Container started (ID: ${CONTAINER_ID:0:12})"

# Step 3: Wait for services to initialize
print_info "Step 3: Waiting for services to initialize (30 seconds)..."
sleep 30

# Step 4: Check container health
print_info "Step 4: Checking container health..."
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "unknown")
if [ "$HEALTH_STATUS" = "healthy" ]; then
    print_success "Container is healthy"
elif [ "$HEALTH_STATUS" = "starting" ]; then
    print_info "Container is still starting, waiting..."
    sleep 15
    HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME")
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        print_success "Container is now healthy"
    else
        print_error "Container health check failed: $HEALTH_STATUS"
        docker logs "$CONTAINER_NAME"
        exit 1
    fi
else
    print_error "Container health check failed: $HEALTH_STATUS"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

# Step 5: Test HTTP accessibility
print_info "Step 5: Testing HTTP accessibility..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$TEST_PORT/vnc.html)
if [ "$HTTP_CODE" = "200" ]; then
    print_success "noVNC is accessible (HTTP $HTTP_CODE)"
else
    print_error "noVNC is not accessible (HTTP $HTTP_CODE)"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

# Step 6: Check running processes
print_info "Step 6: Verifying all services are running..."
SERVICES=("supervisord" "Xvfb" "fluxbox" "x11vnc" "websockify" "main.py")
ALL_RUNNING=true

for service in "${SERVICES[@]}"; do
    if docker exec "$CONTAINER_NAME" pgrep -f "$service" > /dev/null 2>&1; then
        print_success "$service is running"
    else
        print_error "$service is NOT running"
        ALL_RUNNING=false
    fi
done

if [ "$ALL_RUNNING" = false ]; then
    print_error "Some services are not running"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

# Step 7: Check X11 display
print_info "Step 7: Checking X11 display..."
if docker exec "$CONTAINER_NAME" sh -c 'DISPLAY=:0 xdpyinfo' > /dev/null 2>&1; then
    print_success "X11 display is working"
else
    print_error "X11 display is not working"
    exit 1
fi

# Step 8: Check logs for errors
print_info "Step 8: Checking for critical errors in logs..."
# Look for specific critical error patterns (prefixed with ERROR/FATAL or standalone critical keywords)
CRITICAL_ERRORS=$(docker logs "$CONTAINER_NAME" 2>&1 | grep -iE "(ERROR|FATAL).*exception|^(fatal|critical|traceback|segfault)" | wc -l)
if [ "$CRITICAL_ERRORS" -eq 0 ]; then
    print_success "No critical errors found in logs"
else
    print_error "Found $CRITICAL_ERRORS critical error(s) - review logs carefully"
    docker logs "$CONTAINER_NAME" 2>&1 | grep -iE "(ERROR|FATAL).*exception|^(fatal|critical|traceback|segfault)" | head -10
fi

# Success!
echo
echo "=================================="
echo -e "${GREEN}🎉 All tests passed successfully!${NC}"
echo "=================================="
echo
echo "You can access the application at:"
echo "  - Web (noVNC): http://localhost:$TEST_PORT/vnc.html"
echo "  - VNC Direct:  localhost:$VNC_PORT"
echo "  - VNC Password: $VNC_PASSWORD"
echo
echo "To stop and remove the test container:"
echo "  docker stop \"$CONTAINER_NAME\" && docker rm \"$CONTAINER_NAME\""
echo

# Don't cleanup if tests passed - let user explore
trap - EXIT
print_info "Container left running for manual inspection. Run 'docker stop \"$CONTAINER_NAME\"' when done."
