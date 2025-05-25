#!/bin/bash
# Deployment script for Antman project
# Usage: ./deploy.sh <environment> <commit_sha>

set -e

# Configuration
ENVIRONMENT=$1
COMMIT_SHA=$2
PROJECT_NAME="antman"

if [ -z "$ENVIRONMENT" ] || [ -z "$COMMIT_SHA" ]; then
    echo "Usage: $0 <environment> <commit_sha>"
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

echo "🚀 Starting deployment to $ENVIRONMENT..."
echo "📦 Deploying commit: $COMMIT_SHA"

# Connect to server and deploy
ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << EOF
    set -e
    
    echo "📂 Navigating to deployment directory..."
    cd $DEPLOY_PATH
    
    echo "💾 Backing up current deployment..."
    if [ -f .current_sha ]; then
        CURRENT_SHA=\$(cat .current_sha)
        echo \$CURRENT_SHA > .previous_sha
        echo "Backed up current SHA: \$CURRENT_SHA"
    fi
    
    echo "🔄 Updating Docker images..."
    docker pull $DOCKER_REGISTRY:$COMMIT_SHA
    docker tag $DOCKER_REGISTRY:$COMMIT_SHA $DOCKER_REGISTRY:current
    
    echo "🛑 Stopping current containers..."
    docker-compose -f $DOCKER_COMPOSE_FILE down
    
    echo "🗑️ Cleaning up old containers and images..."
    docker system prune -f
    
    echo "🚀 Starting new containers..."
    export DOCKER_IMAGE_TAG=$COMMIT_SHA
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
        echo "❌ Health check failed! Rolling back..."
        docker-compose -f $DOCKER_COMPOSE_FILE down
        if [ -f .previous_sha ]; then
            PREVIOUS_SHA=\$(cat .previous_sha)
            export DOCKER_IMAGE_TAG=\$PREVIOUS_SHA
            docker-compose -f $DOCKER_COMPOSE_FILE up -d
        fi
        exit 1
    fi
    
    echo "🗄️ Running database migrations..."
    docker-compose -f $DOCKER_COMPOSE_FILE exec -T web python manage.py migrate --noinput
    
    echo "📦 Collecting static files..."
    docker-compose -f $DOCKER_COMPOSE_FILE exec -T web python manage.py collectstatic --noinput
    
    echo "💾 Saving deployment information..."
    echo $COMMIT_SHA > .current_sha
    date -u +"%Y-%m-%d %H:%M:%S UTC" > .last_deploy
    
    echo "✅ Deployment completed successfully!"
EOF

echo "🎉 Deployment to $ENVIRONMENT completed!"
