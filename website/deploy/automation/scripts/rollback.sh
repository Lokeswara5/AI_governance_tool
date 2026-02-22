#!/bin/bash
set -e

PREVIOUS_COMMIT=$1
ENVIRONMENT=${2:-production}

echo "Starting rollback to commit $PREVIOUS_COMMIT for environment $ENVIRONMENT"

# Function to handle errors
handle_error() {
    echo "Error: Rollback failed at step $1"
    notify_team "Rollback failed: $1"
    exit 1
}

# Function to notify team
notify_team() {
    if [[ -n $SLACK_WEBHOOK_URL ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$1\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
}

# Rollback ECS service
rollback_ecs() {
    echo "Rolling back ECS service..."

    # Get previous task definition
    prev_task_def=$(aws ecs list-task-definitions \
        --family-prefix "ai-governance-$ENVIRONMENT" \
        --sort DESC \
        --max-items 2 \
        --query 'taskDefinitionArns[1]' \
        --output text) || handle_error "get previous task definition"

    # Update service
    aws ecs update-service \
        --cluster "ai-governance-$ENVIRONMENT" \
        --service "ai-governance-backend-$ENVIRONMENT" \
        --task-definition "$prev_task_def" \
        --force-new-deployment || handle_error "update ECS service"
}

# Rollback S3 frontend
rollback_frontend() {
    echo "Rolling back frontend..."

    # Get previous frontend build
    aws s3 sync \
        "s3://$S3_BUCKET_NAME/builds/$PREVIOUS_COMMIT/" \
        "s3://$S3_BUCKET_NAME/" \
        --delete || handle_error "sync S3 bucket"

    # Invalidate CloudFront cache
    aws cloudfront create-invalidation \
        --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
        --paths "/*" || handle_error "invalidate CloudFront"
}

# Rollback database if needed
rollback_database() {
    echo "Checking database rollback need..."

    # Get latest migration before the failed deployment
    prev_migration=$(aws rds describe-db-snapshots \
        --db-instance-identifier "ai-governance-$ENVIRONMENT" \
        --snapshot-type automated \
        --query 'reverse(DBSnapshots)[0].DBSnapshotIdentifier' \
        --output text)

    if [[ -n $prev_migration ]]; then
        echo "Rolling back database to previous snapshot..."
        aws rds restore-db-instance-from-db-snapshot \
            --db-instance-identifier "ai-governance-$ENVIRONMENT-rollback" \
            --db-snapshot-identifier "$prev_migration" || handle_error "restore database"
    fi
}

# Main rollback process
echo "Starting rollback process..."

# 1. Stop ongoing deployments
aws ecs update-service \
    --cluster "ai-governance-$ENVIRONMENT" \
    --service "ai-governance-backend-$ENVIRONMENT" \
    --desired-count 0 || handle_error "stop service"

# 2. Rollback components
rollback_ecs
rollback_frontend
rollback_database

# 3. Restart service
aws ecs update-service \
    --cluster "ai-governance-$ENVIRONMENT" \
    --service "ai-governance-backend-$ENVIRONMENT" \
    --desired-count 2 || handle_error "restart service"

# 4. Verify rollback
./verify-deployment.sh "$ENVIRONMENT" "$PREVIOUS_COMMIT" || handle_error "verify rollback"

echo "Rollback completed successfully!"
notify_team "Rollback to $PREVIOUS_COMMIT completed successfully for $ENVIRONMENT"