#!/bin/bash
# Rollback script for Antman project
# Usage: ./rollback.sh <environment>

set -e

# Configuration
ENVIRONMENT=$1
PROJECT_NAME="antman"

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 <environment>"
    exit 1
fi

# Environment-specific configuration
case $ENVIRONMENT in
    staging)
        SERVER_HOST=$STAGING_SERVER_HOST
        SERVER_USER=$STAGING_SERVER_USER
        DEPLOY_PATH="/var/www/staging.antman.ai"
        DOCKER_COMPOSE_FILE="docker-compose.staging.yml"
        ;;
    production)
        SERVER_HOST=$PRODUCTION_SERVER_HOST
        SERVER_USER=$PRODUCTION_SERVER_USER
        DEPLOY_PATH="/var/www/antman.ai"
        DOCKER_COMPOSE_FILE="docker-compose.production.yml"
        ;;
    *)
        echo "Invalid environment: $ENVIRONMENT"
        echo "Valid environments: staging, production"
        exit 1
        ;;
esac

echo "⏪ Starting rollback for $ENVIRONMENT..."

# Connect to server and rollback
ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << EOF
    set -e
    
    echo "📂 Navigating to deployment directory..."
    cd $DEPLOY_PATH
    
    # Check if we have a previous deployment
    if [ ! -f .previous_sha ]; then
        echo "❌ No previous deployment found to rollback to!"
        exit 1
    fi
    
    PREVIOUS_SHA=\$(cat .previous_sha)
    CURRENT_SHA=\$(cat .current_sha)
    
    echo "📝 Current deployment: \$CURRENT_SHA"
    echo "⏪ Rolling back to: \$PREVIOUS_SHA"
    
    echo "🛑 Stopping current containers..."
    docker-compose -f $DOCKER_COMPOSE_FILE down
    
    echo "🔄 Switching to previous version..."
    export DOCKER_IMAGE_TAG=\$PREVIOUS_SHA
    
    echo "🚀 Starting previous version containers..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    echo "⏳ Waiting for services to be healthy..."
    sleep 10
    
    echo "🏥 Running health checks..."
    docker-compose -f $DOCKER_COMPOSE_FILE ps
    
    # Check if web service is responding
    MAX_RETRIES=30
    RETRY_COUNT=0
    while [ \$RETRY_COUNT -lt \$MAX_RETRIES ]; do
        if docker-compose -f $DOCKER_COMPOSE_FILE exec -T web curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
            echo "✅ Health check passed!"
            break
        fi
        echo "⏳ Waiting for service to be ready... (\$RETRY_COUNT/\$MAX_RETRIES)"
        sleep 2
        RETRY_COUNT=\$((RETRY_COUNT + 1))
    done
    
    if [ \$RETRY_COUNT -eq \$MAX_RETRIES ]; then
        echo "❌ Rollback failed! Service is not healthy."
        exit 1
    fi
    
    echo "💾 Updating deployment information..."
    # Swap current and previous
    echo \$CURRENT_SHA > .rollback_from_sha
    echo \$PREVIOUS_SHA > .current_sha
    echo \$CURRENT_SHA > .previous_sha
    date -u +"%Y-%m-%d %H:%M:%S UTC" > .last_rollback
    
    echo "✅ Rollback completed successfully!"
    echo "📝 Rolled back from \$CURRENT_SHA to \$PREVIOUS_SHA"
EOF

echo "🎉 Rollback for $ENVIRONMENT completed!"
