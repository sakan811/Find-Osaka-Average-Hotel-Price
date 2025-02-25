#!/bin/bash

# Exit on error
set -e

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker first:"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Export test environment variables
export POSTGRES_DB=test_japan_hotels
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_HOST=localhost
export POSTGRES_PORT=7777

# Set locale and encoding for proper Unicode support
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# Docker container name
CONTAINER_NAME="japan-hotels-test-db"

# Function to ensure container is completely fresh
ensure_fresh_container() {
    echo "Ensuring fresh PostgreSQL container..."
    
    # Stop and remove container if it exists (running or not)
    if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        echo "Removing existing container..."
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
    fi

    # Remove any existing volume to ensure clean state
    docker volume rm ${CONTAINER_NAME}_data 2>/dev/null || true

    echo "Starting new container..."
    # Start new container with a named volume and pass all environment variables
    docker run --name $CONTAINER_NAME \
        -e POSTGRES_USER=$POSTGRES_USER \
        -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
        -e POSTGRES_DB=$POSTGRES_DB \
        -e POSTGRES_INITDB_ARGS="--encoding=UTF8 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8" \
        -e LANG=en_US.UTF-8 \
        -e LC_ALL=en_US.UTF-8 \
        -p $POSTGRES_PORT:5432 \
        -v ${CONTAINER_NAME}_data:/var/lib/postgresql/data \
        -d postgres:latest

    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if docker exec $CONTAINER_NAME pg_isready -U $POSTGRES_USER >/dev/null 2>&1; then
            echo "PostgreSQL is ready!"
            
            # Set client encoding to UTF8
            docker exec -i $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SET client_encoding = 'UTF8';"
            
            return 0
        fi
        echo "Waiting... ($i/30)"
        sleep 1
    done
    echo "Error: PostgreSQL failed to start"
    exit 1
}

# Function to run SQL commands in container with error handling
docker_psql() {
    local retries=3
    local wait_time=2
    local attempt=1
    local result
    local query="$1"
    
    while [ $attempt -le $retries ]; do
        # Capture both stdout and stderr, explicitly specify database
        # Use -c for command and properly escape the query
        result=$(docker exec -i $CONTAINER_NAME psql \
            -U $POSTGRES_USER \
            -d $POSTGRES_DB \
            -v ON_ERROR_STOP=1 \
            --no-align \
            --tuples-only \
            -c "$query" 2>&1)
        
        if [ $? -eq 0 ]; then
            echo "$result"
            return 0
        else
            echo "Attempt $attempt failed: $result"
            if [[ $result == *"deadlock detected"* ]]; then
                echo "Deadlock detected, waiting before retry..."
            fi
            
            if [ $attempt -eq $retries ]; then
                echo "Failed after $retries attempts"
                return 1
            fi
            
            echo "Waiting $wait_time seconds before retry..."
            sleep $wait_time
            wait_time=$((wait_time * 2))
            attempt=$((attempt + 1))
        fi
    done
}

# Function to execute a SQL file in the container
docker_psql_file() {
    local sql_file="$1"
    
    if [ ! -f "$sql_file" ]; then
        echo "Error: SQL file $sql_file does not exist"
        return 1
    fi
    
    # Execute SQL file in container
    cat "$sql_file" | docker exec -i $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -v ON_ERROR_STOP=1
    return $?
}

# Function to cleanup tables
cleanup_tables() {
    echo "Cleaning up tables..."
    docker_psql "
    DO \$\$ 
    BEGIN 
        PERFORM pg_advisory_lock(1);  -- Get exclusive lock to prevent deadlocks
        

        IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'HotelPrice') THEN
            TRUNCATE TABLE \"HotelPrice\" CASCADE;
        END IF;
        IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'JapanHotels') THEN
            TRUNCATE TABLE \"JapanHotels\" CASCADE;
        END IF;
        
        PERFORM pg_advisory_unlock(1);  -- Release the lock
    END \$\$;"
}

# Function to check results with count and sample data
check_results() {
    local table=$1
    local min_expected_rows=$2
    echo "Checking results in $table table..."
    
    # Handle quoted table names properly
    local query_table="$table"
    if [[ "$table" == *\"*\"* ]]; then
        # Table name already has quotes
        query_table="$table"
    elif [[ "$table" =~ [A-Z] ]]; then
        # Table name has uppercase letters, add double quotes
        query_table=\"$table\"
    fi
    
    # Get count of rows with error handling
    local count
    count=$(docker_psql "SELECT COUNT(*) FROM $query_table;" | grep -o '[0-9]\+' || echo "0")
    
    if [ -z "$count" ] || [ "$count" = "0" ]; then
        echo "Error: Failed to get row count or table is empty"
        return 1
    fi
    
    echo "Found $count rows in $table"
    if [ "$count" -lt "$min_expected_rows" ]; then
        echo "Error: Expected at least $min_expected_rows rows, but found $count rows"
        echo "Sample of data found:"
        docker_psql "SELECT * FROM $query_table LIMIT 5;"
        return 1
    fi
    
    # Show sample of data
    echo "Sample of scraped data:"
    docker_psql "SELECT * FROM $query_table LIMIT 5;"
    return 0
}

# Start fresh PostgreSQL container
ensure_fresh_container

# Add parent directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(dirname $(pwd))

# Get current date in YYYY-MM-DD format
CURRENT_DATE=$(date +%Y-%m-%d)
NEXT_DATE=$(date -d "$CURRENT_DATE + 1 day" +%Y-%m-%d)
CURRENT_YEAR=$(date +%Y)
CURRENT_MONTH=$(date +%-m)

# Create temporary .env file for testing
cat > .env.test << EOL
POSTGRES_DB=$POSTGRES_DB
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_HOST=$POSTGRES_HOST
POSTGRES_PORT=$POSTGRES_PORT
EOL

# Run Basic Scraper Test
echo "Running Basic Scraper Test..."
DOTENV_PATH=.env.test python main.py \
  --scraper \
  --city "Tokyo" \
  --country "Japan" \
  --check_in "$CURRENT_DATE" \
  --check_out "$NEXT_DATE" \
  --no_override_env \
  --selected_currency "USD" || { echo "Basic Scraper failed"; exit 1; }

echo "Basic Scraper completed. Checking results..."
check_results \"HotelPrice\" 1 || { echo "Basic Scraper data verification failed"; exit 1; }

# Run Whole Month Scraper Test
echo "Running Whole Month Scraper Test..."
cleanup_tables  # Clean previous scraper results
python main.py \
  --whole_mth \
  --city "Tokyo" \
  --country "Japan" \
  --year "$CURRENT_YEAR" \
  --month "$CURRENT_MONTH" \
  --selected_currency "USD" \
  --no_override_env || { echo "Whole Month Scraper failed"; exit 1; }

echo "Whole Month Scraper completed. Checking results..."
check_results \"HotelPrice\" 20 || { echo "Whole Month Scraper data verification failed"; exit 1; }

# Run Japan Hotel Scraper Test
echo "Running Japan Hotel Scraper Test..."
cleanup_tables  # Clean previous scraper results
python main.py \
  --japan_hotel \
  --prefecture "Hokkaido" \
  --country "Japan" \
  --selected_currency "USD" \
  --start_month "$CURRENT_MONTH" \
  --end_month "$CURRENT_MONTH" \
  --no_override_env || { echo "Japan Hotel Scraper failed"; exit 1; }

echo "Japan Hotel Scraper completed. Checking results..."
check_results \"JapanHotels\" 1 || { echo "Japan Hotel Scraper data verification failed"; exit 1; }

# Example of querying tables with uppercase names
echo "Example of querying HotelPrice table..."
docker_psql "SELECT * FROM \"HotelPrice\" LIMIT 5;"

echo "Example of querying JapanHotels table..."
docker_psql "SELECT * FROM \"JapanHotels\" LIMIT 5;"

# Final cleanup
cleanup_tables
rm -f .env.test  # Remove temporary .env file

# Restore environment
unset POSTGRES_DB
unset POSTGRES_USER
unset POSTGRES_PASSWORD
unset POSTGRES_HOST
unset POSTGRES_PORT
unset PYTHONPATH

echo "All tests completed successfully!" 