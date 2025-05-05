#!/bin/bash

# Set default values
BACKUP_DIR="./database_backups"
FILENAME="sekurah_db_backup_$(date +%Y%m%d_%H%M%S).sql"
CONTAINER_NAME="" # Will be auto-detected if not specified
ENV_FILE=".env"
AUTO_DETECT_CONTAINER=true

# Load environment variables from .env file if it exists
load_env_file() {
  local env_file=$1
  if [[ -f "$env_file" ]]; then
    echo "Loading configuration from $env_file"
    
    # Source the entire .env file to get all variables
    source "$env_file"
  fi
}

# Auto-detect postgres container
detect_postgres_container() {
  # Get a list of all running containers with postgres in the name
  local postgres_containers=$(docker ps --format "{{.Names}}" | grep -E "postgres|postgres_1|postgres_db")
  
  if [ -z "$postgres_containers" ]; then
    echo "No running PostgreSQL containers found"
    return 1
  fi
  
  # If running in production mode, look for prod_postgres first
  if [[ "$ENV_FILE" == *"prod"* ]]; then
    local prod_container=$(echo "$postgres_containers" | grep -E "prod.*postgres" | head -1)
    if [ -n "$prod_container" ]; then
      echo "Auto-detected production PostgreSQL container: $prod_container"
      CONTAINER_NAME=$prod_container
      return 0
    fi
  fi
  
  # If running in dev mode, look for dev_postgres first
  if [[ "$ENV_FILE" == *"dev"* ]]; then
    local dev_container=$(echo "$postgres_containers" | grep -E "dev.*postgres" | head -1)
    if [ -n "$dev_container" ]; then
      echo "Auto-detected development PostgreSQL container: $dev_container"
      CONTAINER_NAME=$dev_container
      return 0
    fi
  fi
  
  # If specific environment container not found, just use the first postgres container
  CONTAINER_NAME=$(echo "$postgres_containers" | head -1)
  echo "Auto-detected PostgreSQL container: $CONTAINER_NAME"
  return 0
}

# Parse command line options
while [[ $# -gt 0 ]]; do
  case $1 in
    --output-dir)
      BACKUP_DIR="$2"
      shift 2
      ;;
    --filename)
      FILENAME="$2"
      shift 2
      ;;
    --container)
      CONTAINER_NAME="$2"
      AUTO_DETECT_CONTAINER=false
      shift 2
      ;;
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo "Backup PostgreSQL database from Docker container to host"
      echo ""
      echo "Options:"
      echo "  --env-file FILE             Path to .env file with configuration (default: .env)"
      echo "  --output-dir DIR            Directory to store backup (default: ./database_backups)"
      echo "  --filename NAME             Backup filename (default: sekurah_db_backup_YYYYMMDD_HHMMSS.sql)"
      echo "  --container NAME            PostgreSQL container name (auto-detected if not specified)"
      echo "  --help                      Display this help message"
      echo ""
      echo "Your .env file should contain the same environment variables used in your Docker setup:"
      echo "POSTGRES_DB=dbname"
      echo "POSTGRES_USER=username"
      echo "POSTGRES_PASSWORD=password"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Load configuration from .env file
load_env_file "$ENV_FILE"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Auto-detect container if no specific container was provided
if [ "$AUTO_DETECT_CONTAINER" = true ]; then
  detect_postgres_container
fi

# Verify container exists and is running
if [ -z "$CONTAINER_NAME" ]; then
  echo "Error: Could not determine PostgreSQL container name"
  echo "Available containers:"
  docker ps --format "{{.Names}}"
  exit 1
fi

CONTAINER_STATUS=$(docker ps -q -f name=$CONTAINER_NAME)

if [ -z "$CONTAINER_STATUS" ]; then
  echo "Error: PostgreSQL container '$CONTAINER_NAME' is not running"
  echo "Available containers:"
  docker ps --format "{{.Names}}"
  exit 1
fi

# Get database credentials (prioritize environment variables over container environment)
if [[ -z "$POSTGRES_DB" || -z "$POSTGRES_USER" || -z "$POSTGRES_PASSWORD" ]]; then
  echo "Getting database credentials from container..."
  DB_NAME=$(docker exec $CONTAINER_NAME printenv POSTGRES_DB)
  DB_USER=$(docker exec $CONTAINER_NAME printenv POSTGRES_USER)
  DB_PASSWORD=$(docker exec $CONTAINER_NAME printenv POSTGRES_PASSWORD)
else
  echo "Using database credentials from environment variables"
  DB_NAME=$POSTGRES_DB
  DB_USER=$POSTGRES_USER
  DB_PASSWORD=$POSTGRES_PASSWORD
fi

if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ]; then
  echo "Error: Could not get database credentials"
  exit 1
fi

echo "Backing up database $DB_NAME from container $CONTAINER_NAME..."
echo "Saving to $BACKUP_DIR/$FILENAME"

# Run pg_dump inside the container and save the output to the host
docker exec -e PGPASSWORD=$DB_PASSWORD $CONTAINER_NAME pg_dump -U $DB_USER -d $DB_NAME > "$BACKUP_DIR/$FILENAME"

if [ $? -eq 0 ]; then
  echo "Backup completed successfully!"
  echo "Backup saved to: $(realpath $BACKUP_DIR/$FILENAME)"
  echo "File size: $(du -h $BACKUP_DIR/$FILENAME | cut -f1)"
else
  echo "Error: Backup failed"
  exit 1
fi

# Create compressed version if backup succeeded
if [ -f "$BACKUP_DIR/$FILENAME" ]; then
  COMPRESSED_FILENAME="$FILENAME.gz"
  gzip -c "$BACKUP_DIR/$FILENAME" > "$BACKUP_DIR/$COMPRESSED_FILENAME"
  echo "Compressed backup saved to: $(realpath $BACKUP_DIR/$COMPRESSED_FILENAME)"
  echo "Compressed size: $(du -h $BACKUP_DIR/$COMPRESSED_FILENAME | cut -f1)"
fi 