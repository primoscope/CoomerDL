#!/bin/bash
# CoomerDL Docker Deployment Test Script
# This script validates both the VNC (Desktop) and WebApp (Heroku/GCP) deployment paths

set -e

# Default to testing both, or allow specific target
TARGET=${1:-all}

echo "🧪 CoomerDL Deployment Verification"
echo "=================================="
echo "Target: $TARGET"
echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${YELLOW}ℹ${NC} $1"; }

# --- FUNCTION: Test VNC Deployment ---
test_vnc() {
    echo
    print_info "Testing Path A: Cloud Desktop (VNC)..."
    IMAGE_NAME="coomerdl-vnc-test"
    CONTAINER_NAME="coomerdl-vnc-val"
    TEST_PORT=18080
    VNC_PORT=15900
    VNC_PASSWORD="TEST-PASSWORD"

    # cleanup old
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

    # Build
    print_info "Building VNC image..."
    if docker build -t "$IMAGE_NAME" . > /dev/null 2>&1; then
        print_success "VNC image built"
    else
        print_error "VNC build failed"
        exit 1
    fi

    # Run
    print_info "Starting VNC container..."
    docker run -d --name "$CONTAINER_NAME" \
        -p "$TEST_PORT":8080 \
        -p "$VNC_PORT":5900 \
        -e VNC_PASSWORD="$VNC_PASSWORD" \
        -e PORT=8080 \
        "$IMAGE_NAME" > /dev/null

    # Wait
    print_info "Waiting for services (20s)..."
    sleep 20

    # 1. Check Processes
    print_info "Verifying services..."
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
        docker logs "$CONTAINER_NAME" | tail -20
        docker rm -f "$CONTAINER_NAME" > /dev/null
        exit 1
    fi

    # 2. Check X11
    if docker exec "$CONTAINER_NAME" sh -c 'DISPLAY=:0 xdpyinfo' > /dev/null 2>&1; then
        print_success "X11 display is active"
    else
        print_error "X11 display failed"
        exit 1
    fi

    # Cleanup
    docker rm -f "$CONTAINER_NAME" > /dev/null
    print_success "VNC Deployment Verified (Deep Check)"
}

# --- FUNCTION: Test WebApp Deployment ---
test_webapp() {
    echo
    print_info "Testing Path B/C: Native Web App (Heroku/GCP)..."
    IMAGE_NAME="coomerdl-web-test"
    CONTAINER_NAME="coomerdl-web-val"
    TEST_PORT=18081

    # cleanup old
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

    # Build
    print_info "Building WebApp image (Dockerfile.webapp)..."
    if docker build -f Dockerfile.webapp -t "$IMAGE_NAME" . > /dev/null 2>&1; then
        print_success "WebApp image built"
    else
        print_error "WebApp build failed"
        exit 1
    fi

    # Run
    print_info "Starting WebApp container..."
    # Note: Dockerfile.webapp uses uvicorn directly
    docker run -d --name "$CONTAINER_NAME" -p "$TEST_PORT":8080 -e PORT=8080 "$IMAGE_NAME" > /dev/null

    # Wait
    print_info "Waiting for Uvicorn (10s)..."
    sleep 10

    # Health Check (using curl inside or outside)
    if curl -s "http://localhost:$TEST_PORT/health" | grep -q "healthy"; then
        print_success "Health endpoint responded"
    else
        print_error "Health check failed"
        docker logs "$CONTAINER_NAME" | tail -10
        docker rm -f "$CONTAINER_NAME" > /dev/null
        exit 1
    fi

    # Cleanup
    docker rm -f "$CONTAINER_NAME" > /dev/null
    print_success "WebApp Deployment Verified"
}

# Main Execution
if [[ "$TARGET" == "all" || "$TARGET" == "vnc" ]]; then
    test_vnc
fi

if [[ "$TARGET" == "all" || "$TARGET" == "web" ]]; then
    test_webapp
fi

echo
echo -e "${GREEN}🎉 All deployment paths verified successfully!${NC}"
