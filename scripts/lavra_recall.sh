#!/bin/bash
#
# Search the knowledge base (.lavra/memory/knowledge.jsonl)
#
# Usage:
#   recall.sh "keyword"                    # Search by keyword
#   recall.sh "keyword" --type learned     # Filter by type
#   recall.sh --recent 10                  # Show latest N entries
#   recall.sh --stats                      # Knowledge base stats
#   recall.sh "keyword" --all              # Include archive
#   recall.sh --topic BD-005               # Filter by epic parent
#

MEMORY_DIR="${CLAUDE_PROJECT_DIR:-.}/.lavra/memory"
KNOWLEDGE_FILE="$MEMORY_DIR/knowledge.jsonl"
ARCHIVE_FILE="$MEMORY_DIR/knowledge.archive.jsonl"

if [[ ! -f "$KNOWLEDGE_FILE" ]]; then
  echo "No knowledge base found at $KNOWLEDGE_FILE"
  exit 0
fi

# Parse args
QUERY=""
TYPE_FILTER=""
RECENT=0
SHOW_STATS=false
INCLUDE_ARCHIVE=false
TOPIC_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type) TYPE_FILTER="$2"; shift 2 ;;
    --recent) RECENT="$2"; shift 2 ;;
    --stats) SHOW_STATS=true; shift ;;
    --all) INCLUDE_ARCHIVE=true; shift ;;
    --topic) TOPIC_ID="$2"; shift 2 ;;
    *) QUERY="$1"; shift ;;
  esac
done

# Stats mode
if $SHOW_STATS; then
  TOTAL=$(wc -l < "$KNOWLEDGE_FILE" | tr -d ' ')
  ARCHIVE_COUNT=0
  [[ -f "$ARCHIVE_FILE" ]] && ARCHIVE_COUNT=$(wc -l < "$ARCHIVE_FILE" | tr -d ' ')

  echo "Knowledge base: $KNOWLEDGE_FILE"
  echo "Active entries: $TOTAL"
  echo "Archived: $ARCHIVE_COUNT"
  echo ""
  echo "By type:"
  python3 -c "
import json, sys
from collections import Counter
types = Counter()
with open('$KNOWLEDGE_FILE') as f:
    for line in f:
        try:
            line = line.strip().strip('\"').replace('\\\\\"', '\"')
            data = json.loads(line)
            types[data.get('type', 'unknown')] += 1
        except: pass
for t, c in types.most_common():
    print(f'  {c} {t}')
" 2>/dev/null
  echo ""
  echo "Top tags:"
  python3 -c "
import json, sys
from collections import Counter
tags = Counter()
with open('$KNOWLEDGE_FILE') as f:
    for line in f:
        try:
            line = line.strip().strip('\"').replace('\\\\\"', '\"')
            data = json.loads(line)
            for tag in data.get('tags', []):
                tags[tag] += 1
        except: pass
for t, c in tags.most_common(15):
    print(f'  {c} {t}')
" 2>/dev/null
  exit 0
fi

# Topic mode -- filter by bead parent
if [[ -n "$TOPIC_ID" ]]; then
  if ! command -v bd &>/dev/null; then
    echo "bd not found -- cannot query topic children"
    exit 1
  fi

  CHILDREN=$(bd list --parent "$TOPIC_ID" --json 2>/dev/null | python3 -c "import sys,json; print('\n'.join([x['id'] for x in json.loads(sys.stdin.read())]))" 2>/dev/null)

  if [[ -z "$CHILDREN" ]]; then
    echo "No children found for topic $TOPIC_ID"
    exit 0
  fi

  for CHILD_ID in $CHILDREN; do
    grep "\"bead\":\"$CHILD_ID\"" "$KNOWLEDGE_FILE" 2>/dev/null
  done | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        line = line.strip().strip('\"').replace('\\\\\"', '\"')
        data = json.loads(line)
        print(f\"{data['type'].upper()}: {data['content']}\")
    except: pass
" 2>/dev/null
  exit 0
fi

# Build input (optionally include archive)
INPUT_FILES="$KNOWLEDGE_FILE"
$INCLUDE_ARCHIVE && [[ -f "$ARCHIVE_FILE" ]] && INPUT_FILES="$ARCHIVE_FILE $KNOWLEDGE_FILE"

# Recent mode
if [[ "$RECENT" -gt 0 ]]; then
  tail -"$RECENT" $INPUT_FILES | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        line = line.strip().strip('\"').replace('\\\\\"', '\"')
        data = json.loads(line)
        print(f\"{data['type'].upper()}: {data['content']}\")
    except: pass
" 2>/dev/null
  exit 0
fi

# Search mode
if [[ -z "$QUERY" ]]; then
  echo "Usage: recall.sh \"keyword\" [--type TYPE] [--recent N] [--stats] [--all] [--topic ID]"
  exit 0
fi

# Grep search with python parsing
RESULTS=$(grep -i "$QUERY" $INPUT_FILES 2>/dev/null)

if [[ -n "$RESULTS" ]]; then
  echo "$RESULTS" | python3 -c "
import sys, json
query = '$QUERY'.lower()
type_filter = '$TYPE_FILTER'
results = []
for line in sys.stdin:
    try:
        line = line.strip().strip('\"').replace('\\\\\"', '\"')
        data = json.loads(line)
        if type_filter and data.get('type') != type_filter:
            continue
        results.append(data)
    except: pass

# Sort by timestamp descending
results.sort(key=lambda x: x.get('ts', 0), reverse=True)

for r in results:
    print(f\"[{r['type'].upper()}] {r['content']}\")
    print(f\"  bead: {r.get('bead', 'N/A')} | {', '.join(r.get('tags', []))}\")
" 2>/dev/null
else
  echo "No matches found for: $QUERY"
fi
