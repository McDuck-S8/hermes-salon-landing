#!/bin/bash
# AI OFM Tribute — Cron Auto-Generator with Style-Specific Models
# Schedule: every 2 hours
# Uses Pollinations.ai (free, no API key)
# 
# Model selection per style (based on 2026-07-18 testing):
#   fantasy    → flux   (best quality, needs --delay 5)
#   anime      → flux   (rate limited, needs --delay 8)
#   realistic  → turbo  (fast, reliable, needs --delay 3)

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

# Select model and delay per style
case $STYLE in
    fantasy)
        MODEL="flux"
        DELAY=5
        ;;
    anime)
        MODEL="flux"
        DELAY=8
        ;;
    realistic)
        MODEL="turbo"
        DELAY=3
        ;;
esac

# Generate session - 5 images per session as requested
python scripts/generate.py --count 5 --style "$STYLE" --model "$MODEL" --delay "$DELAY" 2>&1

echo "Cron run complete: $(date) | style=$STYLE model=$MODEL delay=${DELAY}s"