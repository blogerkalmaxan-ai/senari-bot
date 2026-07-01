#!/bin/sh
# Backup PostgreSQL to ./backups, keep last 14 days.
# Cron example: 0 3 * * *  /path/to/backup.sh
set -e

BACKUP_DIR="$(dirname "$0")/../backups"
mkdir -p "$BACKUP_DIR"
STAMP=$(date +%Y%m%d_%H%M%S)
FILE="$BACKUP_DIR/senari_$STAMP.sql.gz"

docker compose exec -T db pg_dump -U "${DB_USER:-senari}" "${DB_NAME:-senari}" \
  | gzip > "$FILE"

echo "Backup saved: $FILE"

# Retention: delete backups older than 14 days
find "$BACKUP_DIR" -name 'senari_*.sql.gz' -mtime +14 -delete
