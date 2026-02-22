#!/bin/bash
set -e

ENVIRONMENT_URL=$1
MAX_RETRIES=30
RETRY_INTERVAL=10

echo "Running smoke tests against $ENVIRONMENT_URL"

# Function to check endpoint health
check_health() {
    local url=$1
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url/health")
    [[ $response == "200" ]]
}

# Function to test API endpoints
test_endpoint() {
    local url=$1
    local endpoint=$2
    local method=${3:-GET}
    local expected_status=${4:-200}

    echo "Testing $method $endpoint..."
    response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url$endpoint")

    if [[ $response == "$expected_status" ]]; then
        echo "✓ $endpoint returned $response as expected"
        return 0
    else
        echo "✗ $endpoint returned $response, expected $expected_status"
        return 1
    fi
}

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
for i in $(seq 1 $MAX_RETRIES); do
    if check_health "$ENVIRONMENT_URL"; then
        echo "Deployment is ready!"
        break
    fi

    if [[ $i == $MAX_RETRIES ]]; then
        echo "Deployment failed to become ready"
        exit 1
    fi

    echo "Waiting for deployment... ($i/$MAX_RETRIES)"
    sleep $RETRY_INTERVAL
done

# Test critical endpoints
test_endpoint "$ENVIRONMENT_URL" "/api/health" "GET" "200"
test_endpoint "$ENVIRONMENT_URL" "/api/docs" "GET" "200"
test_endpoint "$ENVIRONMENT_URL" "/api/metrics" "GET" "200"

# Test frontend static files
echo "Testing frontend static files..."
if curl -s "$ENVIRONMENT_URL" | grep -q "AI Governance Tool"; then
    echo "✓ Frontend is working"
else
    echo "✗ Frontend check failed"
    exit 1
fi

echo "All smoke tests passed!"