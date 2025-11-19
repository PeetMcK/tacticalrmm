#!/bin/zsh

################################################################################
# Installomator Version Detection Script (v2 - Using App-Auto-Patch Method)
#
# Purpose: Detects available versions for all Installomator labels
# Output: JSON file with version data for TacticalRMM consumption
# Platform: macOS (uses osascript, xpath, xmllint)
#
# Usage: ./detect_installomator_versions_v2.zsh [output_file]
################################################################################

# Configuration
INSTALLOMATOR_REPO="https://github.com/Installomator/Installomator"
TARBALL_URL="${INSTALLOMATOR_REPO}/archive/refs/heads/main.tar.gz"
WORK_DIR=$(mktemp -d)
OUTPUT_FILE="${1:-installomator_versions.json}"
FRAGMENTS_DIR="${WORK_DIR}/Installomator-main/fragments"
LABELS_DIR="${FRAGMENTS_DIR}/labels"
FUNCTIONS_FILE="${FRAGMENTS_DIR}/functions.sh"
TEST_MODE=${TEST_MODE:-0}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_LABELS=0
SUCCESS_COUNT=0
FAILED_COUNT=0
SKIPPED_COUNT=0

# Cleanup on exit
cleanup() {
    echo -e "${BLUE}Cleaning up temporary files...${NC}"
    rm -rf "$WORK_DIR"
}
trap cleanup EXIT

echo -e "${BLUE}[INFO]${NC} Starting Installomator version detection..."
echo -e "${BLUE}[INFO]${NC} Downloading Installomator..."

# Download and extract
if ! curl -fsSL "$TARBALL_URL" | tar -xz -C "$WORK_DIR" 2>/dev/null; then
    echo -e "${RED}[ERROR]${NC} Failed to download Installomator"
    exit 1
fi

echo -e "${GREEN}[SUCCESS]${NC} Installomator downloaded"

# Validate
if [[ ! -f "$FUNCTIONS_FILE" ]]; then
    echo -e "${RED}[ERROR]${NC} Functions file not found"
    exit 1
fi

# Count labels
TOTAL_LABELS=$(ls -1 "$LABELS_DIR"/*.sh 2>/dev/null | wc -l | tr -d ' ')
echo -e "${GREEN}[SUCCESS]${NC} Found ${TOTAL_LABELS} labels"

# Get Installomator version
INSTALLOMATOR_VERSION=$(grep -m1 "^VERSION=" "${WORK_DIR}/Installomator-main/Installomator.sh" | cut -d'=' -f2 | tr -d '"' || echo "unknown")

# Source functions ONCE (like App-Auto-Patch does)
echo -e "${BLUE}[INFO]${NC} Loading Installomator functions..."
source "$FUNCTIONS_FILE"
echo -e "${GREEN}[SUCCESS]${NC} Functions loaded"

# Initialize JSON
JSON_LABELS="["
FIRST=true

echo -e "${BLUE}[INFO]${NC} Processing labels..."

CURRENT=0
for label_file in "$LABELS_DIR"/*.sh; do
    CURRENT=$((CURRENT + 1))
    label_name=$(basename "$label_file" .sh)

    # Test mode
    if [[ $TEST_MODE -eq 1 ]] && [[ $CURRENT -gt 10 ]]; then
        echo -e "${YELLOW}[WARNING]${NC} Test mode: stopping after 10 labels"
        break
    fi

    echo -n "[${CURRENT}/${TOTAL_LABELS}] ${label_name}... "

    # Read fragment
    fragment=$(cat "$label_file")

    # Check if fragment has appNewVersion
    if ! echo "$fragment" | grep -q "appNewVersion"; then
        echo -e "${YELLOW}⊘${NC} No appNewVersion"
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))

        [[ "$FIRST" == false ]] && JSON_LABELS+=","
        FIRST=false
        JSON_LABELS+=$(cat <<JSON
{
  "name": "${label_name}",
  "version": null,
  "success": false,
  "error": "No appNewVersion defined"
}
JSON
)
        continue
    fi

    # Evaluate fragment (App-Auto-Patch method)
    # Wrap in case statement and eval
    caseStatement="
case ${label_name} in
    ${fragment}
esac
"

    # Clear previous values
    unset appNewVersion name

    # Try to evaluate (catch errors)
    if eval "$caseStatement" 2>/dev/null; then
        if [[ -n "${appNewVersion:-}" ]]; then
            # Clean version string
            appNewVersion=$(echo "${appNewVersion}" | sed 's/[^a-zA-Z0-9.-]*$//g')

            echo -e "${GREEN}✓${NC} ${appNewVersion}"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

            [[ "$FIRST" == false ]] && JSON_LABELS+=","
            FIRST=false
            JSON_LABELS+=$(cat <<JSON
{
  "name": "${label_name}",
  "version": "${appNewVersion}",
  "success": true,
  "error": null
}
JSON
)
        else
            echo -e "${RED}✗${NC} appNewVersion not populated"
            FAILED_COUNT=$((FAILED_COUNT + 1))

            [[ "$FIRST" == false ]] && JSON_LABELS+=","
            FIRST=false
            JSON_LABELS+=$(cat <<JSON
{
  "name": "${label_name}",
  "version": null,
  "success": false,
  "error": "appNewVersion not populated after eval"
}
JSON
)
        fi
    else
        echo -e "${RED}✗${NC} Eval failed"
        FAILED_COUNT=$((FAILED_COUNT + 1))

        [[ "$FIRST" == false ]] && JSON_LABELS+=","
        FIRST=false
        JSON_LABELS+=$(cat <<JSON
{
  "name": "${label_name}",
  "version": null,
  "success": false,
  "error": "Fragment evaluation failed"
}
JSON
)
    fi

    # Clean up for next iteration
    unset appNewVersion name
done

JSON_LABELS+="]"

# Generate final JSON
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$OUTPUT_FILE" <<JSON
{
  "generated_at": "${TIMESTAMP}",
  "installomator_version": "${INSTALLOMATOR_VERSION}",
  "total_labels": ${TOTAL_LABELS},
  "successful": ${SUCCESS_COUNT},
  "failed": ${FAILED_COUNT},
  "skipped": ${SKIPPED_COUNT},
  "labels": ${JSON_LABELS}
}
JSON

echo ""
echo "================================"
echo "        SUMMARY REPORT"
echo "================================"
echo "Total Labels:    ${TOTAL_LABELS}"
echo -e "${GREEN}Successful:      ${SUCCESS_COUNT}${NC}"
echo -e "${RED}Failed:          ${FAILED_COUNT}${NC}"
echo -e "${YELLOW}Skipped:         ${SKIPPED_COUNT}${NC}"
echo "================================"
echo "Output File:     ${OUTPUT_FILE}"
echo "File Size:       $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "================================"
echo -e "${GREEN}[SUCCESS]${NC} Version detection complete!"
