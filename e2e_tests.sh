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

# Test CREATE operation
test_create() {
    echo "Testing URL creation..."
    response=$(curl -s -X POST -H "Content-Type: application/json" \
         -d '{"originalUrl":"https://example.com"}' \
         $BASE_URL/shorturl/test1)
    
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
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 15
    
    # Run tests
    test_create
    test_read
    test_update
    test_delete
    
    log_success "All E2E tests completed successfully!"
}

main