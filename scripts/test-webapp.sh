#!/bin/bash

# CoomerDL Web Application Test Script
# Tests the complete web application stack

echo "🧪 CoomerDL Web Application Test Suite"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Check Python version
echo "Test 1: Python version check"
python3 --version > /dev/null 2>&1
test_result $? "Python 3 is installed"
echo ""

# Test 2: Check required Python packages
echo "Test 2: Python dependencies"
python3 -c "import fastapi" > /dev/null 2>&1
test_result $? "FastAPI is installed"

python3 -c "import uvicorn" > /dev/null 2>&1
test_result $? "Uvicorn is installed"

python3 -c "import pydantic" > /dev/null 2>&1
test_result $? "Pydantic is installed"
echo ""

# Test 3: Check backend structure
echo "Test 3: Backend structure"
[ -d "backend/api" ]
test_result $? "backend/api directory exists"

[ -f "backend/api/main.py" ]
test_result $? "backend/api/main.py exists"

[ -f "backend/config/settings.py" ]
test_result $? "backend/config/settings.py exists"
echo ""

# Test 4: Check frontend structure
echo "Test 4: Frontend structure"
[ -d "frontend/src" ]
test_result $? "frontend/src directory exists"

[ -f "frontend/package.json" ]
test_result $? "frontend/package.json exists"

[ -f "frontend/vite.config.ts" ]
test_result $? "frontend/vite.config.ts exists"
echo ""

# Test 5: Check Docker files
echo "Test 5: Docker configuration"
[ -f "Dockerfile.webapp" ]
test_result $? "Dockerfile.webapp exists"

[ -f "docker-compose.yml" ]
test_result $? "docker-compose.yml exists"

[ -f ".dockerignore" ]
test_result $? ".dockerignore exists"
echo ""

# Test 6: Check deployment files
echo "Test 6: Deployment configuration"
[ -f "cloudbuild.yaml" ]
test_result $? "cloudbuild.yaml exists"

[ -f "app.yaml" ]
test_result $? "app.yaml exists"

[ -f "scripts/deploy-gcp.sh" ]
test_result $? "scripts/deploy-gcp.sh exists"

[ -x "scripts/deploy-gcp.sh" ]
test_result $? "scripts/deploy-gcp.sh is executable"
echo ""

# Test 7: Check documentation
echo "Test 7: Documentation"
[ -f "DEPLOYMENT.md" ]
test_result $? "DEPLOYMENT.md exists"

[ -f "API.md" ]
test_result $? "API.md exists"

[ -f ".env.example" ]
test_result $? ".env.example exists"
echo ""

# Test 8: Backend Python syntax check
echo "Test 8: Python syntax validation"
python3 -m py_compile backend/api/main.py > /dev/null 2>&1
test_result $? "backend/api/main.py syntax is valid"

python3 -m py_compile backend/config/settings.py > /dev/null 2>&1
test_result $? "backend/config/settings.py syntax is valid"
echo ""

# Test 9: Backend import check
echo "Test 9: Backend imports"
python3 -c "from backend.config.settings import settings; print('OK')" > /dev/null 2>&1
test_result $? "Backend settings can be imported"

python3 -c "from backend.api.main import app; print('OK')" > /dev/null 2>&1
test_result $? "Backend app can be imported"
echo ""

# Test 10: API health check (if server is running)
echo "Test 10: API health check"
if command -v curl &> /dev/null; then
    # Try to start server in background
    echo "  Starting test server..."
    python3 -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8081 > /dev/null 2>&1 &
    SERVER_PID=$!
    sleep 5
    
    # Check health endpoint
    HEALTH_RESPONSE=$(curl -s http://127.0.0.1:8081/health 2>/dev/null || echo "failed")
    
    if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
        test_result 0 "API health endpoint responds correctly"
    else
        test_result 1 "API health endpoint not responding"
    fi
    
    # Cleanup
    kill $SERVER_PID > /dev/null 2>&1 || true
    sleep 1
else
    echo -e "${YELLOW}⊘ SKIP${NC}: curl not available for API test"
fi
echo ""

# Summary
echo "======================================"
echo "Test Results Summary"
echo "======================================"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Web application is ready.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the errors above.${NC}"
    exit 1
fi
