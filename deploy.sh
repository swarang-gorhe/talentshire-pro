#!/bin/bash

# ============================================================================
# Talentshire Platform - Complete Deployment & Demo Script
# ============================================================================
# This script handles deployment, testing, and live demonstration
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Talentshire"
DOCKER_COMPOSE_FILE="docker-compose.yml"
API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:5173"
DEMO_MODE=false
CLEANUP=false

# Detect docker compose command (legacy `docker-compose` or plugin `docker compose`)
COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
fi

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ ${GREEN}$1${BLUE} ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
}

print_section() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}▶ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=1
    
    print_info "Waiting for service at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_success "Service is ready!"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Service failed to start after ${max_attempts} attempts"
    return 1
}

# ============================================================================
# Deployment Functions
# ============================================================================

check_prerequisites() {
    print_section "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker found"
    
    # Check Docker Compose (either legacy or plugin)
    if [ -z "$COMPOSE_CMD" ]; then
        print_error "Docker Compose is not available. Install 'docker-compose' or enable the 'docker compose' plugin."
        exit 1
    fi
    print_success "Using compose command: $COMPOSE_CMD"
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed"
        exit 1
    fi
    print_success "curl found"
    
    # Check if ports are available
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port 8000 is already in use"
        exit 1
    fi
    print_success "Port 8000 is available"
    
    if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port 5173 is already in use"
        exit 1
    fi
    print_success "Port 5173 is available"
    
    if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port 5432 is already in use"
        exit 1
    fi
    print_success "Port 5432 is available"
}

build_images() {
    print_section "Building Docker Images"
    
    $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE build --no-cache
    
    print_success "Docker images built successfully"
}

start_services() {
    print_section "Starting Services"
    
    $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE up -d
    
    print_success "Services started in background"
    print_info "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_info "Waiting for PostgreSQL..."
    sleep 5
    
    # Wait for Backend
    print_info "Waiting for Backend API..."
    wait_for_service "$API_URL/docs"
    
    # Wait for Frontend
    print_info "Waiting for Frontend..."
    wait_for_service "$FRONTEND_URL"
}

show_service_status() {
    print_section "Service Status"
    
    $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE ps
    
    print_info "Services running:"
    echo -e "${GREEN}Backend API:${NC} $API_URL"
    echo -e "${GREEN}Frontend:${NC} $FRONTEND_URL"
    echo -e "${GREEN}PgAdmin:${NC} http://localhost:5050"
    echo -e "${GREEN}API Docs:${NC} $API_URL/docs"
}

# ============================================================================
# Demo Functions
# ============================================================================

demo_api_endpoints() {
    print_section "Testing API Endpoints"
    
    print_info "1. Testing API Health Check"
    curl -s "$API_URL/docs" | grep -q "openapi" && print_success "API is healthy" || print_error "API health check failed"
    
    print_info "2. Creating a Test"
    TEST_RESPONSE=$(curl -s -X POST "$API_URL/api/tests" \
        -H "Content-Type: application/json" \
        -d '{
            "test_name": "JavaScript Fundamentals Demo",
            "description": "A comprehensive test covering JavaScript basics",
            "duration_minutes": 60,
            "total_marks": 100,
            "passing_marks": 40,
            "status": "draft"
        }')
    
    echo "$TEST_RESPONSE" | grep -q "test_id" && print_success "Test created" || print_error "Failed to create test"
    
    TEST_ID=$(echo "$TEST_RESPONSE" | grep -o '"test_id":"[^"]*"' | cut -d'"' -f4 | head -1)
    
    if [ -z "$TEST_ID" ]; then
        print_error "Could not extract test ID"
        return 1
    fi
    
    print_success "Test ID: $TEST_ID"
    
    print_info "3. Fetching Tests"
    curl -s "$API_URL/api/tests" | grep -q "test_name" && print_success "Tests fetched" || print_error "Failed to fetch tests"
    
    print_info "4. Getting Specific Test"
    curl -s "$API_URL/api/tests/$TEST_ID" | grep -q "test_name" && print_success "Test retrieved" || print_error "Failed to retrieve test"
}

demo_frontend() {
    print_section "Frontend Verification"
    
    print_info "Frontend is running at: $FRONTEND_URL"
    print_info "Open in browser to interact with:"
    echo -e "  ${GREEN}• Test Management${NC}"
    echo -e "  ${GREEN}• Candidate Portal${NC}"
    echo -e "  ${GREEN}• Test Taking Interface${NC}"
    echo -e "  ${GREEN}• Report Generation${NC}"
}

demo_database() {
    print_section "Database Verification"
    
    print_info "PostgreSQL is running"
    print_info "PgAdmin is available at: http://localhost:5050"
    print_info "Credentials:"
    echo -e "  ${GREEN}Email:${NC} admin@talentshire.com"
    echo -e "  ${GREEN}Password:${NC} admin@123"
    
    print_info "\nDatabase connection:"
    echo -e "  ${GREEN}Host:${NC} localhost"
    echo -e "  ${GREEN}Port:${NC} 5432"
    echo -e "  ${GREEN}Database:${NC} talentshire"
    echo -e "  ${GREEN}User:${NC} postgres"
    echo -e "  ${GREEN}Password:${NC} admin@123"
}

run_live_demo() {
    print_header "🎬 LIVE DEMO - Complete Platform Showcase"
    
    # Check if Python demo script exists
    if [ -f "demo.py" ]; then
        print_section "Running Python Demo Script"
        
        print_info "Launching interactive demo..."
        python3 demo.py
    else
        print_section "Running Shell Demo"
        
        demo_api_endpoints
        
        print_section "Demo Complete!"
        
        echo -e "\n${GREEN}✨ Your Talentshire platform is running!${NC}\n"
        
        print_info "Available Services:"
        echo -e "  ${BLUE}• API Documentation:${NC} $API_URL/docs"
        echo -e "  ${BLUE}• Frontend Application:${NC} $FRONTEND_URL"
        echo -e "  ${BLUE}• Database Management:${NC} http://localhost:5050"
        echo -e "  ${BLUE}• OpenAPI JSON:${NC} $API_URL/openapi.json"
        
        print_info "Next steps:"
        echo -e "  1. Open ${BLUE}$FRONTEND_URL${NC} in your browser"
        echo -e "  2. Try creating and managing tests"
        echo -e "  3. Review API at ${BLUE}$API_URL/docs${NC}"
        echo -e "  4. Manage database via ${BLUE}http://localhost:5050${NC}"
    fi
}

# ============================================================================
# Cleanup Functions
# ============================================================================

stop_services() {
    print_section "Stopping Services"
    
    $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE down
    
    print_success "Services stopped"
}

cleanup_containers() {
    print_section "Cleaning Up"
    
    $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE down -v
    
    print_success "Containers and volumes removed"
}

# ============================================================================
# Main Script
# ============================================================================

main() {
    print_header "🚀 Talentshire Platform - Deployment & Demo"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --demo)
                DEMO_MODE=true
                shift
                ;;
            --cleanup)
                CLEANUP=true
                shift
                ;;
            --stop)
                stop_services
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
    
    # Check prerequisites
    check_prerequisites
    
    # Build and start
    build_images
    start_services
    show_service_status
    
    # Run demo if requested
    if [ "$DEMO_MODE" = true ]; then
        run_live_demo
    else
        print_section "Setup Complete!"
        echo -e "\n${GREEN}✨ Your Talentshire platform is ready!${NC}\n"
        echo -e "To run the demo: ${BLUE}./deploy.sh --demo${NC}\n"
        echo -e "To stop services: ${BLUE}./deploy.sh --stop${NC}\n"
    fi
}

# Run main function
main "$@"
