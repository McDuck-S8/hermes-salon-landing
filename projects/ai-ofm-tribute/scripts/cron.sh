#!/bin/bash
# AI OFM Tribute — Cron Auto-Generator
# Schedule: every 2 hours
# Uses Pollinations.ai (free, no API key)

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR" || exit 1

# Pick style round-robin
STYLES=("fantasy" "anime" "realistic")
STYLE_INDEX_FILE="content/.style_index"

if [ -f "$STYLE_INDEX_FILE" ]; then
    IDX=$(cat "$STYLE_INDEX_FILE")
    IDX=$(( (IDX + 1) % 3 ))
else
    IDX=0
fi
echo -n "$IDX" > "$STYLE_INDEX_FILE"
STYLE="${STYLES[$IDX]}"

# Generate session
python scripts/generate.py --count 3 --style "$STYLE" 2>&1

echo "Cron run complete: $(date)"
