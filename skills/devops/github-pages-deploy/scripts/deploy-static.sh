#!/usr/bin/env bash
# ============================================================
# deploy-static.sh — универсальный деплой статического проекта
# на GitHub Pages, Vercel, Netlify или Cloudflare Pages.
#
# Использование:
#   bash deploy-static.sh <project-dir> [--gh-pages|--vercel|--netlify|--cf-pages]
#
# Пример:
#   bash deploy-static.sh projects/famp-prep --gh-pages
# ============================================================
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-D:/Portable_Soft/hermes}"
PROJECT_DIR="${1:-}"
TARGET="${2:---gh-pages}"
PROJECT_NAME=""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

if [ -z "$PROJECT_DIR" ]; then
    error "Укажи директорию проекта: bash deploy-static.sh projects/famp-prep"
fi
if [ ! -d "$HERMES_HOME/$PROJECT_DIR" ]; then
    error "Директория $PROJECT_DIR не найдена в $HERMES_HOME"
fi

echo "============================================"
echo "  Деплой проекта: $PROJECT_DIR"
echo "  Цель:           $TARGET"
echo "============================================"

if [ "$TARGET" = "--gh-pages" ] || [ "$TARGET" = "--gh" ]; then
    PROJECT_NAME=$(basename "$PROJECT_DIR")
    DOCS_PATH="$HERMES_HOME/docs/$PROJECT_NAME"
    log "Копирую проект в docs/$PROJECT_NAME ..."
    mkdir -p "$DOCS_PATH"
    cp -r "$HERMES_HOME/$PROJECT_DIR/"* "$DOCS_PATH/"
    log "Файлы скопированы. Для git push выполни:"
    echo ""
    echo "  cd $HERMES_HOME"
    echo "  git add docs/$PROJECT_NAME/"
    echo "  git commit -m \"deploy: $PROJECT_NAME\""
    echo "  git push"
    echo ""
    echo "  # Включить GitHub Pages (один раз):"
    echo "  gh api repos/<owner>/<repo>/pages --method POST \\"
    echo "    -f source[branch]=main \\"
    echo "    -f source[path]=/docs \\"
    echo "    -H \"Accept: application/vnd.github+json\""
fi

if [ "$TARGET" = "--vercel" ]; then
    command -v vercel >/dev/null 2>&1 || error "Vercel CLI не установлен: npm i -g vercel"
    cd "$HERMES_HOME/$PROJECT_DIR"
    vercel --prod --yes
    log "Деплой на Vercel готов"
fi

if [ "$TARGET" = "--netlify" ]; then
    command -v netlify >/dev/null 2>&1 || error "Netlify CLI не установлен: npm i -g netlify-cli"
    cd "$HERMES_HOME/$PROJECT_DIR"
    netlify deploy --prod --dir=.
    log "Деплой на Netlify готов"
fi

if [ "$TARGET" = "--cf-pages" ] || [ "$TARGET" = "--cf" ]; then
    command -v wrangler >/dev/null 2>&1 || error "Wrangler не установлен: npm i -g wrangler"
    cd "$HERMES_HOME/$PROJECT_DIR"
    wrangler pages deploy . --project-name="$PROJECT_NAME"
    log "Деплой на Cloudflare Pages готов"
fi

log "Скрипт завершён."
