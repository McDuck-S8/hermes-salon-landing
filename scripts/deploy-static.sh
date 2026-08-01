#!/usr/bin/env bash
# ============================================================
# deploy-static.sh — универсальный деплой статического проекта
# на GitHub Pages, Vercel, Netlify или Cloudflare Pages.
# 
# Использование:
#   ./deploy-static.sh <project-dir> [--gh-pages|--vercel|--netlify|--cf-pages]
#
# Пример:
#   ./deploy-static.sh projects/famp-prep --gh-pages
#
# Зависимости: gh CLI (для GitHub Pages), node (для Vercel/Netlify)
# ============================================================
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-D:/Portable_Soft/hermes}"
PROJECT_DIR="${1:-}"
TARGET="${2:---gh-pages}"
PROJECT_NAME=""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# --- Проверки ---
if [ -z "$PROJECT_DIR" ]; then
    error "Укажи директорию проекта: ./deploy-static.sh projects/famp-prep"
fi

if [ ! -d "$HERMES_HOME/$PROJECT_DIR" ]; then
    error "Директория $PROJECT_DIR не найдена в $HERMES_HOME"
fi

echo "============================================"
echo "  Деплой проекта: $PROJECT_DIR"
echo "  Цель:           $TARGET"
echo "============================================"

# --- GitHub Pages ---
if [ "$TARGET" = "--gh-pages" ] || [ "$TARGET" = "--gh" ]; then
    # Определяем имя проекта из пути
    PROJECT_NAME=$(basename "$PROJECT_DIR")
    DOCS_PATH="$HERMES_HOME/docs/$PROJECT_NAME"

    log "Копирую проект в docs/$PROJECT_NAME ..."
    mkdir -p "$HERMES_HOME/docs/$PROJECT_NAME"
    cp -r "$HERMES_HOME/$PROJECT_DIR/"* "$DOCS_PATH/"

    log "Файлы скопированы. Для завершения выполни:"
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
    echo ""
    echo "  После деплоя: https://<owner>.github.io/<repo>/$PROJECT_NAME/"
fi

# --- Vercel ---
if [ "$TARGET" = "--vercel" ]; then
    if ! command -v vercel &> /dev/null; then
        error "Vercel CLI не установлен. Установи: npm i -g vercel"
    fi
    log "Деплою на Vercel ..."
    cd "$HERMES_HOME/$PROJECT_DIR"
    vercel --prod --yes
    log "Готово! Vercel даст URL."
fi

# --- Netlify ---
if [ "$TARGET" = "--netlify" ]; then
    if ! command -v netlify &> /dev/null; then
        error "Netlify CLI не установлен. Установи: npm i -g netlify-cli"
    fi
    log "Деплою на Netlify ..."
    cd "$HERMES_HOME/$PROJECT_DIR"
    netlify deploy --prod --dir=.
    log "Готово!"
fi

# --- Cloudflare Pages ---
if [ "$TARGET" = "--cf-pages" ] || [ "$TARGET" = "--cf" ]; then
    if ! command -v wrangler &> /dev/null; then
        error "Wrangler CLI не установлен. Установи: npm i -g wrangler"
    fi
    log "Деплою на Cloudflare Pages ..."
    cd "$HERMES_HOME/$PROJECT_DIR"
    wrangler pages deploy . --project-name="$PROJECT_NAME"
    log "Готово!"
fi

log "Скрипт завершён."
