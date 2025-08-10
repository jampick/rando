#!/bin/bash

# Grim Observer - Conan Exiles Log Monitor
# macOS shell script wrapper

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GRIM_SCRIPT="$SCRIPT_DIR/grim_observer.py"
LOG_FILE=""
MAP="exiled"
CONFIG_FILE="$SCRIPT_DIR/config.json"

# Function to show usage
show_usage() {
    echo "Usage: $0 [--map exiled|siptah] [--log-file \"path/to/ConanSandbox.log\"] [--config \"path/to/config.json\"]"
    echo ""
    echo "Examples:"
    echo "  $0 --map exiled"
    echo "  $0 --map siptah"
    echo "  $0 --map exiled --log-file \"/path/to/ConanSandbox.log\""
    echo "  $0 --map siptah --config \"/path/to/custom_config.json\""
    echo ""
    echo "Note: If --log-file is not specified, the default path from secrets will be used."
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --map)
            MAP="$2"
            shift 2
            ;;
        -map)
            MAP="$2"
            shift 2
            ;;
        --log-file)
            LOG_FILE="$2"
            shift 2
            ;;
        -f)
            LOG_FILE="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

echo "Starting Grim Observer..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.6+ and try again"
    exit 1
fi

# Load secrets by map
SECRETS_FILE="$SCRIPT_DIR/secrets/secrets.$MAP.sh"
if [[ -f "$SECRETS_FILE" ]]; then
    echo "[GrimObserver][INFO] Loading secrets for $MAP map..."
    source "$SECRETS_FILE"
    echo "[GrimObserver][INFO] Loaded secrets from $SECRETS_FILE"
    
    # Display loaded environment variables
    if [[ -n "$DISCORD_WEBHOOK_URL" ]]; then
        echo "[GrimObserver][INFO] Discord webhook configured for $MAP map"
    fi
    if [[ -n "$MAP_NAME" ]]; then
        echo "[GrimObserver][INFO] Map name: $MAP_NAME"
    fi
    if [[ -n "$MAP_DESCRIPTION" ]]; then
        echo "[GrimObserver][INFO] Map description: $MAP_DESCRIPTION"
    fi
    
    # Set default log file from secrets if not provided via CLI
    if [[ -z "$LOG_FILE" ]] && [[ -n "$LOG_FILE_PATH" ]]; then
        LOG_FILE="$LOG_FILE_PATH"
        echo "[GrimObserver][INFO] Using default log file from secrets: $LOG_FILE"
    fi
else
    echo "[GrimObserver][WARN] Secrets file not found: $SECRETS_FILE"
    echo "[GrimObserver][WARN] Using default configuration"
fi

# Check if log file path is available
if [[ -z "$LOG_FILE" ]]; then
    echo "[GrimObserver][ERROR] Missing log file path"
    echo ""
    show_usage
    exit 1
fi

# Check for map-specific configs
MAP_CONFIG_DIR="$SCRIPT_DIR/configs/$MAP"
if [[ -d "$MAP_CONFIG_DIR" ]]; then
    echo "[GrimObserver][INFO] Found map-specific configs directory: $MAP_CONFIG_DIR"
    
    # Check for map-specific config.json
    if [[ -f "$MAP_CONFIG_DIR/config.json" ]] && [[ "$CONFIG_FILE" == "$SCRIPT_DIR/config.json" ]]; then
        CONFIG_FILE="$MAP_CONFIG_DIR/config.json"
        echo "[GrimObserver][INFO] Using map-specific config: $CONFIG_FILE"
    fi
    
    # Check for map-specific events or other configs
    if [[ -f "$MAP_CONFIG_DIR/events.json" ]]; then
        echo "[GrimObserver][INFO] Found map-specific events: $MAP_CONFIG_DIR/events.json"
    fi
else
    echo "[GrimObserver][INFO] No map-specific configs found, using defaults"
fi

# Run the observer
echo ""
echo "[GrimObserver] Running log observer"
echo "   LOG:    $LOG_FILE"
echo "   MAP:    $MAP"
echo "   CONFIG: $CONFIG_FILE"
echo "   Press Ctrl+C to stop monitoring"
echo ""

python3 "$GRIM_SCRIPT" --log-file "$LOG_FILE" --map "$MAP" --config "$CONFIG_FILE" --verbose
