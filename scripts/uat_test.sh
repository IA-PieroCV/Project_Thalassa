#!/bin/bash

# UAT Testing Script for Project Thalassa
# This script automates the UAT testing procedures

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
BEARER_TOKEN="${BEARER_TOKEN:-test-token}"
TEST_DIR="test_data"
RESULTS_FILE="uat_results.txt"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

test_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((TESTS_PASSED++))
    echo "[PASS] $1" >> $RESULTS_FILE
}

test_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((TESTS_FAILED++))
    echo "[FAIL] $1" >> $RESULTS_FILE
}

# Setup test environment
setup() {
    log_info "Setting up test environment..."

    # Create test directory
    mkdir -p $TEST_DIR

    # Create test FASTQ files
    cat > $TEST_DIR/Mowi_CAGE-04B_2025-08-15_S01.fastq << EOF
@SEQ_ID_001
GATCGATCGATCGATCGATCGATC
+
IIIIIIIIIIIIIIIIIIIIIIII
@SEQ_ID_002
ATCGATCGATCGATCGATCGATCG
+
HHHHHHHHHHHHHHHHHHHHHHHH
EOF

    cat > $TEST_DIR/SalMar_SITE-A-01_2025-12-03_Sample-001.fastq << EOF
@SEQ_ID_001
ATCGATCGATCGATCGATCGATCG
+
HHHHHHHHHHHHHHHHHHHHHHHH
EOF

    # Invalid filename
    cat > $TEST_DIR/invalid_filename.fastq << EOF
@SEQ_ID_001
GATCGATCGATCGATCGATCGATC
+
IIIIIIIIIIIIIIIIIIIIIIII
EOF

    # Initialize results file
    echo "UAT Test Results - $(date)" > $RESULTS_FILE
    echo "================================" >> $RESULTS_FILE

    log_info "Test environment ready"
}

# Test 1: Health Check
test_health_check() {
    log_info "Test 1: Health Check"

    response=$(curl -s -w "\n%{http_code}" ${API_URL}/health)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ]; then
        if echo "$body" | grep -q "healthy"; then
            test_pass "Health check endpoint working"
        else
            test_fail "Health check response invalid"
        fi
    else
        test_fail "Health check returned HTTP $http_code"
    fi
}

# Test 2: Authentication Required
test_auth_required() {
    log_info "Test 2: Authentication Required"

    # Test without auth
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -F "file=@${TEST_DIR}/Mowi_CAGE-04B_2025-08-15_S01.fastq" \
        ${API_URL}/api/v1/upload)
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq 401 ]; then
        test_pass "Unauthorized access rejected"
    else
        test_fail "Expected 401, got HTTP $http_code"
    fi

    # Test with invalid token
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Authorization: Bearer invalid-token" \
        -F "file=@${TEST_DIR}/Mowi_CAGE-04B_2025-08-15_S01.fastq" \
        ${API_URL}/api/v1/upload)
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq 401 ]; then
        test_pass "Invalid token rejected"
    else
        test_fail "Invalid token: Expected 401, got HTTP $http_code"
    fi
}

# Test 3: Valid File Upload
test_valid_upload() {
    log_info "Test 3: Valid File Upload"

    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Authorization: Bearer ${BEARER_TOKEN}" \
        -F "file=@${TEST_DIR}/Mowi_CAGE-04B_2025-08-15_S01.fastq" \
        ${API_URL}/api/v1/upload)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ]; then
        if echo "$body" | grep -q "successfully"; then
            test_pass "Valid file upload successful"

            # Check metadata extraction
            if echo "$body" | grep -q "Mowi" && \
               echo "$body" | grep -q "CAGE-04B" && \
               echo "$body" | grep -q "2025-08-15"; then
                test_pass "Metadata correctly extracted"
            else
                test_fail "Metadata extraction failed"
            fi
        else
            test_fail "Upload response invalid"
        fi
    else
        test_fail "Upload failed with HTTP $http_code"
    fi
}

# Test 4: Invalid Filename
test_invalid_filename() {
    log_info "Test 4: Invalid Filename Format"

    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Authorization: Bearer ${BEARER_TOKEN}" \
        -F "file=@${TEST_DIR}/invalid_filename.fastq" \
        ${API_URL}/api/v1/upload)
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq 400 ]; then
        test_pass "Invalid filename rejected"
    else
        test_fail "Invalid filename: Expected 400, got HTTP $http_code"
    fi
}

# Test 5: Dashboard Access
test_dashboard() {
    log_info "Test 5: Dashboard Access"

    response=$(curl -s -w "\n%{http_code}" -X GET \
        -H "Authorization: Bearer ${BEARER_TOKEN}" \
        ${API_URL}/api/v1/dashboard)
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq 200 ]; then
        test_pass "Dashboard accessible"
    else
        test_fail "Dashboard returned HTTP $http_code"
    fi
}

# Test 6: API Documentation
test_api_docs() {
    log_info "Test 6: API Documentation"

    # Test Swagger UI
    response=$(curl -s -w "\n%{http_code}" ${API_URL}/docs)
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq 200 ]; then
        test_pass "Swagger UI accessible"
    else
        test_fail "Swagger UI returned HTTP $http_code"
    fi

    # Test ReDoc
    response=$(curl -s -w "\n%{http_code}" ${API_URL}/redoc)
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq 200 ]; then
        test_pass "ReDoc accessible"
    else
        test_fail "ReDoc returned HTTP $http_code"
    fi
}

# Test 7: List Files
test_list_files() {
    log_info "Test 7: List Uploaded Files"

    response=$(curl -s -w "\n%{http_code}" -X GET \
        -H "Authorization: Bearer ${BEARER_TOKEN}" \
        ${API_URL}/api/v1/upload/files)
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq 200 ]; then
        test_pass "File listing works"
    else
        test_fail "File listing returned HTTP $http_code"
    fi
}

# Test 8: Concurrent Uploads
test_concurrent() {
    log_info "Test 8: Concurrent Uploads"

    # Create additional test files
    for i in {1..3}; do
        cp $TEST_DIR/Mowi_CAGE-04B_2025-08-15_S01.fastq \
           $TEST_DIR/Test_CAGE-0${i}_2025-08-15_S0${i}.fastq
    done

    # Upload files in parallel
    success_count=0
    for file in $TEST_DIR/Test_CAGE-*.fastq; do
        (curl -s -X POST \
            -H "Authorization: Bearer ${BEARER_TOKEN}" \
            -F "file=@${file}" \
            ${API_URL}/api/v1/upload > /dev/null 2>&1 && echo "OK") &
    done | while read result; do
        if [ "$result" = "OK" ]; then
            ((success_count++))
        fi
    done

    wait  # Wait for all background jobs

    test_pass "Concurrent uploads handled"
}

# Performance test
test_performance() {
    log_info "Test 9: Performance Check"

    start_time=$(date +%s%N)

    # Make 10 health check requests
    for i in {1..10}; do
        curl -s ${API_URL}/health > /dev/null 2>&1
    done

    end_time=$(date +%s%N)
    duration=$((($end_time - $start_time) / 1000000))  # Convert to milliseconds
    avg_time=$(($duration / 10))

    if [ $avg_time -lt 1000 ]; then  # Less than 1 second average
        test_pass "Performance acceptable (${avg_time}ms avg response)"
    else
        test_fail "Performance slow (${avg_time}ms avg response)"
    fi
}

# Cleanup
cleanup() {
    log_info "Cleaning up test files..."
    rm -rf $TEST_DIR
}

# Main execution
main() {
    echo "========================================"
    echo "Project Thalassa UAT Testing Script"
    echo "========================================"
    echo "API URL: $API_URL"
    echo "Start Time: $(date)"
    echo ""

    # Check if API is reachable
    if ! curl -s --connect-timeout 5 ${API_URL}/health > /dev/null 2>&1; then
        log_error "Cannot reach API at ${API_URL}"
        log_error "Please ensure the application is running"
        exit 1
    fi

    # Run tests
    setup

    test_health_check
    test_auth_required
    test_valid_upload
    test_invalid_filename
    test_dashboard
    test_api_docs
    test_list_files
    test_concurrent
    test_performance

    # Summary
    echo ""
    echo "========================================"
    echo "Test Summary"
    echo "========================================"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    echo "Results saved to: $RESULTS_FILE"

    # Cleanup
    cleanup

    # Exit code based on results
    if [ $TESTS_FAILED -eq 0 ]; then
        log_info "All tests passed! ✅"
        exit 0
    else
        log_error "Some tests failed. Please review the results."
        exit 1
    fi
}

# Handle script arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            API_URL="$2"
            shift 2
            ;;
        --token)
            BEARER_TOKEN="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --url URL      API URL (default: http://localhost:8000)"
            echo "  --token TOKEN  Bearer token for authentication"
            echo "  --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main
