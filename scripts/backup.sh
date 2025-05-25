#!/bin/bash
# Database backup script for Antman project

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="antman_production"
DB_USER="antman"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "🗄️ Starting database backup..."

# Create database backup
pg_dump -h db -U $DB_USER -d $DB_NAME > $BACKUP_DIR/backup_${TIMESTAMP}.sql

# Compress the backup
gzip $BACKUP_DIR/backup_${TIMESTAMP}.sql

echo "✅ Database backup completed: backup_${TIMESTAMP}.sql.gz"

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "🧹 Old backups cleaned up"
