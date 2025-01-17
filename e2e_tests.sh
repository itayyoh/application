#!/bin/bash

# Exit on any error
set -e

# Base URL
BASE_URL="http://localhost:80"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_success() {
    echo -e "${GREEN}$1${NC}"
}

log_error() {
    echo -e "${RED}$1${NC}"
}

# Wait for services to be ready
wait_for_service() {
    local retries=30
    local wait_time=2
    echo "Waiting for services to be ready..."
    
    while [ $retries -gt 0 ]; do
        if curl -s http://localhost:80 > /dev/null; then
            echo "Services are ready!"
            return 0
        fi
        echo "Waiting for services... ($retries attempts left)"
        sleep $wait_time
        retries=$((retries-1))
    done
    
    log_error "Services failed to become ready in time"
    return 1
}

# Test CREATE operation
test_create() {
    echo "Testing URL creation..."
    response=$(curl -s -X POST -H "Content-Type: application/json" \
         -d '{"originalUrl":"https://example.com"}' \
         $BASE_URL/shorturl/test1)
    
    echo "Create Response: $response"
    if [[ $response == *"created"* ]]; then
        log_success "✓ Create test passed"
        return 0
    else
        log_error "✗ Create test failed"
        log_error "Response: $response"
        return 1
    fi
}

# Test READ operation
test_read() {
    echo "Testing URL retrieval..."
    response=$(curl -s $BASE_URL/shorturl/test1)
    
    echo "Read Response: $response"
    if [[ $response == *"example.com"* ]]; then
        log_success "✓ Read test passed"
        return 0
    else
        log_error "✗ Read test failed"
        log_error "Response: $response"
        return 1
    fi
}

# Test UPDATE operation
test_update() {
    echo "Testing URL update..."
    response=$(curl -s -X PUT -H "Content-Type: application/json" \
         -d '{"originalUrl":"https://updated-example.com"}' \
         $BASE_URL/shorturl/test1)
    
    echo "Update Response: $response"
    if [[ $response == *"updated"* ]]; then
        log_success "✓ Update test passed"
        return 0
    else
        log_error "✗ Update test failed"
        log_error "Response: $response"
        return 1
    fi
}

# Test DELETE operation
test_delete() {
    echo "Testing URL deletion..."
    response=$(curl -s -X DELETE $BASE_URL/shorturl/test1)
    
    echo "Delete Response: $response"
    if [[ $response == *"deleted"* ]]; then
        log_success "✓ Delete test passed"
        return 0
    else
        log_error "✗ Delete test failed"
        log_error "Response: $response"
        return 1
    fi
}

# Main test execution
main() {
    echo "Starting E2E tests..."
    
    # Wait for services with better feedback
    wait_for_service || exit 1
    
    # Run tests
    test_create || exit 1
    test_read || exit 1
    test_update || exit 1
    test_delete || exit 1
    
    log_success "All E2E tests completed successfully!"
}

main