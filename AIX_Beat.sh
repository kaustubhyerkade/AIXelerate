#!/bin/ksh
# ------------------------------------------------------------------
# AIX-BEAT: A lightweight Filebeat alternative in Shell | Kaustubh yerkade 25-Sep-2025
# ------------------------------------------------------------------

# --- CONFIGURATION ---
LOG_FILE="/var/log/application.log"
STATE_FILE="/tmp/aixbeat.state"
HOSTNAME=$(hostname)

# TARGET: Where to send logs? 
# Option 1: Logstash HTTP Input
TARGET_URL="http://your-logstash-server:8080"
# Option 2: Elasticsearch Direct
# TARGET_URL="http://your-es-server:9200/my-index/_doc"

# --- HEADERS ---
# We use ndjson (newline delimited JSON) or standard JSON depending on the receiver.
CONTENT_TYPE="Content-Type: application/json"

# --- FUNCTIONS ---

# Function to escape special JSON characters to prevent breakage
escape_json_string() {
    echo "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g;'
}

# Function to ship the log
ship_log() {
    local raw_line="$1"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local safe_line=$(escape_json_string "$raw_line")

    # Construct JSON payload (mimicking Filebeat structure)
    # We include @timestamp, host.name, log.file.path, and message
    json_payload="{
        \"@timestamp\": \"$timestamp\",
        \"host\": { \"name\": \"$HOSTNAME\" },
        \"log\": { \"file\": { \"path\": \"$LOG_FILE\" } },
        \"message\": \"$safe_line\"
    }"

    # Send via CURL
    # -s = silent, -X POST, --data-binary preserves newlines if needed
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "$CONTENT_TYPE" -d "$json_payload" "$TARGET_URL")

    if [ "$response" -ne 200 ] && [ "$response" -ne 201 ]; then
        echo "ERROR: Failed to ship log. HTTP Code: $response" >&2
    fi
}

# --- MAIN LOGIC ---

echo "Starting AIX-Beat for file: $LOG_FILE"
echo "Shipping to: $TARGET_URL"

# Check if file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: Log file $LOG_FILE not found."
    exit 1
fi

# The 'tail -f' Loop
# standard AIX tail -f follows the file descriptor (inode).
# Using line-buffered output to pipe into the loop.

tail -f "$LOG_FILE" | while read -r line; do
    # Skip empty lines
    if [ -z "$line" ]; then
        continue
    fi
    
    ship_log "$line"
done
