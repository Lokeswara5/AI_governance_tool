#!/bin/bash
set -e

ENVIRONMENT=$1
IMAGE_TAG=$2
MAX_RETRIES=30
RETRY_INTERVAL=10

# Verify ECS service stability
verify_ecs_service() {
    local cluster="ai-governance-$ENVIRONMENT"
    local service="ai-governance-backend-$ENVIRONMENT"

    echo "Verifying ECS service stability..."
    for i in $(seq 1 $MAX_RETRIES); do
        # Get service status
        status=$(aws ecs describe-services \
            --cluster "$cluster" \
            --services "$service" \
            --query 'services[0].deployments[0].rolloutState' \
            --output text)

        if [[ $status == "COMPLETED" ]]; then
            echo "ECS service is stable"
            return 0
        fi

        if [[ $status == "FAILED" ]]; then
            echo "ECS service deployment failed"
            return 1
        fi

        echo "Waiting for ECS service... ($i/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    done

    echo "Timeout waiting for ECS service"
    return 1
}

# Verify CloudFront distribution
verify_cloudfront() {
    local distribution_id=$CLOUDFRONT_DISTRIBUTION_ID

    echo "Verifying CloudFront distribution..."
    for i in $(seq 1 $MAX_RETRIES); do
        status=$(aws cloudfront get-distribution \
            --id "$distribution_id" \
            --query 'Distribution.Status' \
            --output text)

        if [[ $status == "Deployed" ]]; then
            echo "CloudFront distribution is deployed"
            return 0
        fi

        echo "Waiting for CloudFront... ($i/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    done

    echo "Timeout waiting for CloudFront"
    return 1
}

# Verify running containers
verify_containers() {
    local cluster="ai-governance-$ENVIRONMENT"
    local service="ai-governance-backend-$ENVIRONMENT"

    echo "Verifying container images..."
    tasks=$(aws ecs list-tasks \
        --cluster "$cluster" \
        --service-name "$service" \
        --query 'taskArns[]' \
        --output text)

    for task in $tasks; do
        image=$(aws ecs describe-tasks \
            --cluster "$cluster" \
            --tasks "$task" \
            --query 'tasks[0].containers[0].imageDigest' \
            --output text)

        if [[ $image != *"$IMAGE_TAG"* ]]; then
            echo "Task $task is not running expected image"
            return 1
        fi
    done

    echo "All containers are running correct image"
    return 0
}

# Main verification
echo "Starting deployment verification for $ENVIRONMENT"

verify_ecs_service || exit 1
verify_cloudfront || exit 1
verify_containers || exit 1

echo "Deployment verification successful!"