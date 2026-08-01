#!/bin/bash
# AI OFM Tribute — Cron Script with Style-Specific Models
# 
# Place at: projects/ai-ofm-tribute/scripts/cron.sh
# Called by: scripts/ai-ofm-generate.sh (cron wrapper)
#
# Cycles through styles: fantasy → anime → realistic
# Uses optimal model per style based on 2026-07-18 testing

STYLE_INDEX_FILE="content/.style_index"
mkdir -p content

# Read current style index (0=fantasy, 1=anime, 2=realistic)
if [ -f "$STYLE_INDEX_FILE" ]; then
    style_idx=$(cat "$STYLE_INDEX_FILE")
else
    style_idx=0
fi

# Cycle: 0 → 1 → 2 → 0
case $style_idx in
    0)
        style="fantasy"
        model="flux"
        delay=5
        ;;
    1)
        style="anime"
        model="flux"
        delay=8
        ;;
    2)
        style="realistic"
        model="turbo"
        delay=3
        ;;
esac

# Update index for next run
next_idx=$(( (style_idx + 1) % 3 ))
echo "$next_idx" > "$STYLE_INDEX_FILE"

# Run generator with style-specific settings
cd "$(dirname "$0")/.." || exit 1
python scripts/generate.py --count 5 --style "$style" --model "$model" --delay "$delay"

# Log
echo "$(date): Generated session - style=$style model=$model delay=${delay}s"