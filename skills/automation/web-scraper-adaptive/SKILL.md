---
name: web-scraper-adaptive
category: automation
description: |
  Адаптивный веб-скрапер на базе Scrapling — обход Cloudflare, ротация прокси (SOCKS5/HTTP),
  адаптивный парсинг через CSS/XPath/регулярки, CLI для запуска из терминала и интеграции в пайплайны.
  Интегрирован в pipeline free_traffic_launch для сбора контента из бесплатных источников трафика.
version: 1.0.0
tags:
  - web-scraping
  - scrapling
  - cloudflare-bypass
  - proxy
  - socks5
  - cli
  - adaptive-parsing
  - free-traffic
dependencies:
  - python: ">=3.10"
  - packages:
      - scrapling>=0.1.0
      - httpx>=0.27.0
      - click>=8.1.0
      - pyyaml>=6.0
      - rich>=13.0
      - loguru>=0.7.0
      - tenacity>=8.0
      - pydantic>=2.0
      - lxml>=4.9
      - cssselect>=1.2
      - cssselect2>=0.7
      - html2text>=2024.0
      - readability-lxml>=0.8
      - python-dotenv>=1.0
      - pydantic-settings>=2.0
      - rich-click>=1.7
      - playwright>=1.40
      - undetected-chromedriver>=3.5
  system:
    - playwright-chromium: ">=1.40"
    - google-chrome: ">=120"
    - python3: ">=3.10"
conflicts: []
provides:
  - cli: scraper-adaptive
  - python-module: scraper_adaptive
  - module: scraper_adaptive.scraper
  - module: scraper_adaptive.cli
  - module: scraper_adaptive.config
  - module: scraper_adaptive.parsers
  - module: scraper_adaptive.proxy
  - module: scraper_adaptive.browser
  - function: scraper_adaptive.scraper.scrape
  - function: scraper_adaptive.scraper.scrape_batch
  - function: scraper_adaptive.scraper.extract
  - class: scraper_adaptive.scraper.AdaptiveScraper
  - class: scraper_adaptive.proxy.ProxyManager
  - class: scraper_adaptive.browser.BrowserManager
  - class: scraper_adaptive.parsers.AdaptiveParser
  - cli: scraper-adaptive
entry_points:
  - scraper-adaptive
  - scraper-adaptive scrape
  - scraper-adaptive batch
  - scraper-adaptive config
  - scraper-adaptive proxy
  - scraper-adaptive browser
config_schema:
  proxy:
    enabled: true
    default: "socks5://127.0.0.1:10806"
    rotation_interval: 300
    health_check_interval: 60
    max_failures: 3
    timeout: 30
    sources:
      - "socks5://127.0.0.1:10806"
      - "http://127.0.0.1:8080"
  cloudflare:
    enabled: true
    challenge_timeout: 30
    challenge_retries: 3
    use_undetected_chrome: true
    headless: true
    browser_args:
      - "--disable-blink-features=AutomationControlled"
      - "--disable-dev-shm-usage"
      - "--no-sandbox"
  parser:
    default_parser: "auto"
    parsers:
      - "css"
      - "xpath"
      - "regex"
      - "readability"
      - "html2text"
      - "auto"
    auto_detect: true
    readability_threshold: 100
  browser:
    engine: "playwright"
    headless: true
    viewport:
      width: 1920
      height: 1080
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    timeout: 60000
    wait_until: "networkidle"
  scraper:
    default_timeout: 30
    max_retries: 3
    retry_delay: 2
    follow_redirects: true
    max_redirects: 10
    verify_ssl: false
    headers:
      Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
      Accept-Language: "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
      Accept-Encoding: "gzip, deflate, br"
      Connection: "keep-alive"
      Upgrade-Insecure-Requests: "1"
      Sec-Fetch-Dest: "document"
      Sec-Fetch-Mode: "navigate"
      Sec-Fetch-Site: "none"
      Sec-Fetch-User: "?1"
  output:
    default_format: "json"
    formats:
      - "json"
      - "jsonl"
      - "csv"
      - "markdown"
      - "html"
      - "text"
    output_dir: "./output"
    filename_template: "{domain}_{timestamp}.{ext}"
  logging:
    level: "INFO"
    format: "json"
    file: "./logs/scraper.log"
    rotation: "10 MB"
    retention: "7 days"
  proxy_file: "./config/proxies.txt"
  config_file: "./config/scraper.yaml"
  browser_profile_dir: "./browser_profiles"
  cache_dir: "./cache"
  output_dir: "./output"
  log_dir: "./logs"
hooks:
  pre_run:
    - "scraper_adaptive.hooks.pre_run_check"
  post_run:
    - "scraper_adaptive.hooks.post_run_cleanup"
  on_error:
    - "scraper_adaptive.hooks.on_error_notify"
examples:
  - name: "Basic scrape"
    description: "Basic single URL scraping with auto-detection"
    command: "scraper-adaptive scrape https://example.com"
  - name: "Scrape with Cloudflare bypass"
    description: "Scrape Cloudflare-protected site using undetected Chrome"
    command: "scraper-adaptive scrape https://example.com --cloudflare --browser"
  - name: "Batch scrape with proxy rotation"
    description: "Batch scrape multiple URLs with SOCKS5 proxy rotation"
    command: "scraper-adaptive batch urls.txt --proxy socks5://127.0.0.1:10806 --rotate-proxy --output results.jsonl"
  - name: "Extract with CSS selector"
    description: "Extract specific elements using CSS selector"
    command: "scraper-adaptive scrape https://example.com --selector '.product-title' --format json"
  - name: "Extract with XPath"
    description: "Extract using XPath expression"
    command: "scraper-adaptive scrape https://example.com --xpath '//div[@class=\"product\"]//h2' --format jsonl"
  - name: "Extract article content"
    description: "Extract article content using readability algorithm"
    command: "scraper-adaptive scrape https://example.com/article --parser readability --format markdown"
  - name: "Batch with proxy rotation and Cloudflare bypass"
    description: "Full pipeline for scraping protected sites with proxy rotation"
    command: "scraper-adaptive batch urls.txt --cloudflare --browser --proxy socks5://127.0.0.1:10806 --rotate-proxy --retries 5 --output results.jsonl --format jsonl"
  - name: "Browser automation"
    description: "Use browser automation for JavaScript-heavy sites"
    command: "scraper-adaptive browser https://example.com --wait-for '.content' --click '#load-more' --scroll 3 --output page.html"
  - name: "Proxy management"
    description: "Manage proxy list and test proxies"
    command: "scraper-adaptive proxy test --file proxies.txt --url https://httpbin.org/ip"
  - name: "Configuration"
    description: "Show current configuration"
    command: "scraper-adaptive config show"
  - name: "Free traffic launch integration"
    description: "Integration with free_traffic_launch pipeline"
    command: "scraper-adaptive batch free_traffic_sources.txt --cloudflare --proxy socks5://127.0.0.1:10806 --output free_traffic_content.jsonl --format jsonl"
configuration:
  description: |
    Конфигурация хранится в ./config/scraper.yaml или в переменных окружения.
    Переменные окружения имеют приоритет над конфигурационным файлом.
    
    Переменные окружения:
    - SCRAPER_PROXY: Основной прокси (по умолчанию socks5://127.0.0.1:10806)
    - SCRAPER_PROXY_FILE: Файл со списком прокси
    - SCRAPER_PROXY_ROTATION_INTERVAL: Интервал ротации прокси (сек)
    - SCRAPER_CLOUDFLARE_ENABLED: Включить обход Cloudflare (true/false)
    - SCRAPER_CLOUDFLARE_TIMEOUT: Таймаут обхода Cloudflare (сек)
    - SCRAPER_BROWSER_ENGINE: Движок браузера (playwright/undetected-chrome)
    - SCRAPER_BROWSER_HEADLESS: Безголовый режим (true/false)
    - SCRAPER_DEFAULT_TIMEOUT: Таймаут запроса по умолчанию (сек)
    - SCRAPER_MAX_RETRIES: Максимальное количество попыток
    - SCRAPER_OUTPUT_DIR: Директория для выходных файлов
    - SCRAPER_OUTPUT_FORMAT: Формат вывода по умолчанию
    - SCRAPER_LOG_LEVEL: Уровень логирования
    - SCRAPER_LOG_FILE: Файл логов
    - SCRAPER_PROXY_HEALTH_CHECK: Проверка здоровья прокси (true/false)
    - SCRAPER_BROWSER_HEADLESS: Headless режим браузера
    - SCRAPER_BROWSER_ENGINE: Движок браузера
    - SCRAPER_PARSER_DEFAULT: Парсер по умолчанию
    - SCRAPER_OUTPUT_FORMAT: Формат вывода по умолчанию
    - SCRAPER_PROXY_FILE: Файл со списком прокси
    - SCRAPER_BROWSER_PROFILE_DIR: Директория профилей браузера
    - SCRAPER_CACHE_DIR: Директория кэша
    - SCRAPER_OUTPUT_DIR: Директория вывода
    - SCRAPER_LOG_DIR: Директория логов
    - SCRAPER_CONFIG_FILE: Путь к конфигурационному файлу
    - SCRAPER_PROXY_ENABLED: Включить прокси
    - SCRAPER_CLOUDFLARE_CHALLENGE_TIMEOUT: Таймаут челленджа Cloudflare
    - SCRAPER_CLOUDFLARE_CHALLENGE_RETRIES: Попытки прохождения челленджа
    - SCRAPER_BROWSER_VIEWPORT_WIDTH: Ширина viewport
    - SCRAPER_BROWSER_VIEWPORT_HEIGHT: Высота viewport
    - SCRAPER_BROWSER_USER_AGENT: User-Agent
    - SCRAPER_BROWSER_TIMEOUT: Таймаут браузера (мс)
    - SCRAPER_BROWSER_WAIT_UNTIL: Условие ожидания (load/domcontentloaded/networkidle)
    - SCRAPER_SCRAPER_FOLLOW_REDIRECTS: Следовать редиректам
    - SCRAPER_SCRAPER_MAX_REDIRECTS: Максимум редиректов
    - SCRAPER_SCRAPER_VERIFY_SSL: Проверять SSL
    - SCRAPER_PARSER_AUTO_DETECT: Автоопределение парсера
    - SCRAPER_PARSER_READABILITY_THRESHOLD: Порог читаемости
    - SCRAPER_OUTPUT_FILENAME_TEMPLATE: Шаблон имени файла
    - SCRAPER_LOG_FORMAT: Формат логов (json/text)
    - SCRAPER_LOG_ROTATION: Ротация логов
    - SCRAPER_LOG_RETENTION: Хранение логов
  examples:
    - name: "Minimal config"
      config: |
        proxy:
          enabled: true
          default: "socks5://127.0.0.1:10806"
        cloudflare:
          enabled: true
        output:
          output_dir: "./output"
    - name: "Full config with proxy rotation"
      config: |
        proxy:
          enabled: true
          default: "socks5://127.0.0.1:10806"
          rotation_interval: 300
          health_check_interval: 60
          max_failures: 3
          timeout: 30
          sources:
            - "socks5://127.0.0.1:10806"
            - "http://127.0.0.1:8080"
        cloudflare:
          enabled: true
          challenge_timeout: 30
          challenge_retries: 3
          use_undetected_chrome: true
          headless: true
        browser:
          engine: "playwright"
          headless: true
          viewport:
            width: 1920
            height: 1080
          user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          timeout: 60000
          wait_until: "networkidle"
        parser:
          default_parser: "auto"
          auto_detect: true
        scraper:
          default_timeout: 30
          max_retries: 3
          retry_delay: 2
        output:
          default_format: "jsonl"
          output_dir: "./output"
          filename_template: "{domain}_{timestamp}.{ext}"
        logging:
          level: "INFO"
          format: "json"
          file: "./logs/scraper.log"
          rotation: "10 MB"
          retention: "7 days"
integration:
  free_traffic_launch:
    description: "Интеграция в pipeline free_traffic_launch для сбора контента из бесплатных источников трафика"
    commands:
      - name: "scrape_free_traffic_sources"
        description: "Сбор контента из списка бесплатных источников трафика"
        command: "scraper-adaptive batch free_traffic_sources.txt --cloudflare --proxy socks5://127.0.0.1:10806 --output free_traffic_content.jsonl --format jsonl"
      - name: "scrape_competitor_content"
        description: "Сбор контента конкурентов для анализа"
        command: "scraper-adaptive batch competitor_urls.txt --cloudflare --browser --proxy socks5://127.0.0.1:10806 --output competitor_content.jsonl --format jsonl"
      - name: "extract_article_content"
        description: "Извлечение контента статей через readability"
        command: "scraper-adaptive batch article_urls.txt --parser readability --format markdown --output articles/"
      - name: "scrape_social_media"
        description: "Скрапинг социальных сетей с обходом Cloudflare"
        command: "scraper-adaptive batch social_urls.txt --cloudflare --browser --proxy socks5://127.0.0.1:10806 --output social_content.jsonl --format jsonl"
  free_traffic_launch_steps:
    - step: "collect_sources"
      description: "Сбор списка URL бесплатных источников трафика"
      command: "free-traffic-launch collect-sources --output free_traffic_sources.txt"
    - step: "scrape_content"
      description: "Скрапинг контента из источников"
      command: "scraper-adaptive batch free_traffic_sources.txt --cloudflare --proxy socks5://127.0.0.1:10806 --output free_traffic_content.jsonl --format jsonl"
    - step: "extract_content"
      description: "Извлечение чистого контента статей"
      command: "scraper-adaptive batch free_traffic_content.jsonl --parser readability --format markdown --output articles/"
    - step: "analyze_content"
      description: "Анализ контента для поиска трендов"
      command: "free-traffic-launch analyze-content --input articles/ --output trends.json"
    - step: "generate_content"
      description: "Генерация контента на основе трендов"
      command: "free-traffic-launch generate-content --trends trends.json --output content/"
    - step: "publish_content"
      description: "Публикация контента в каналы"
      command: "free-traffic-launch publish --content content/ --channels telegram,linkedin,twitter"
  integration_points:
    - name: "free_traffic_launch.collect_sources"
      description: "Сбор URL источников"
    - name: "free_traffic_launch.scrape_content"
      description: "Скрапинг контента через web-scraper-adaptive"
    - name: "free_traffic_launch.extract_content"
      description: "Извлечение чистого контента"
    - name: "free_traffic_launch.analyze"
      description: "Анализ трендов"
    - name: "free_traffic_launch.generate"
      description: "Генерация контента"
    - name: "free_traffic_launch.publish"
      description: "Публикация"
hooks_impl:
  pre_run_check:
    - "Проверка доступности прокси"
    - "Проверка доступности браузера (Playwright/Chrome)"
    - "Проверка конфигурации"
    - "Создание необходимых директорий"
  post_run_cleanup:
    - "Закрытие браузеров"
    - "Закрытие соединений с прокси"
    - "Очистка временных файлов"
    - "Ротация логов"
  on_error_notify:
    - "Логирование ошибки"
    - "Уведомление в Telegram (если настроено)"
    - "Сохранение состояния для восстановления"
documentation:
  - name: "CLI Reference"
    path: "docs/cli.md"
  - name: "Configuration"
    path: "docs/config.md"
  - name: "Parsers Guide"
    path: "docs/parsers.md"
  - name: "Proxy Management"
    path: "docs/proxy.md"
  - name: "Cloudflare Bypass"
    path: "docs/cloudflare.md"
  - name: "Browser Automation"
    path: "docs/browser.md"
  - name: "Integration Guide"
    path: "docs/integration.md"
  - name: "Free Traffic Launch Integration"
    path: "docs/free_traffic_integration.md"
  - name: "Examples"
    path: "docs/examples.md"
  - name: "Troubleshooting"
    path: "docs/troubleshooting.md"
changelog:
  - version: "1.0.0"
    date: "2026-07-30"
    changes:
      - "Initial release"
      - "Adaptive parsing with CSS, XPath, Regex, Readability, HTML2Text"
      - "Cloudflare bypass via undetected-chromedriver and Playwright"
      - "SOCKS5/HTTP proxy support with rotation"
      - "CLI with scrape, batch, config, proxy, browser commands"
      - "Integration with free_traffic_launch pipeline"
      - "Proxy rotation and health checks"
      - "Multiple output formats: JSON, JSONL, CSV, Markdown, HTML, Text"
      - "Multiple parsers: CSS, XPath, Regex, Readability, HTML2Text, Auto-detect"
      - "Browser automation with Playwright and undetected-chromedriver"
      - "Cloudflare challenge bypass with retries"
      - "Proxy rotation and health checks"
      - "Multiple output formats"
      - "Configuration via YAML and environment variables"
      - "Logging with rotation and retention"
      - "Browser automation with wait conditions, clicks, scrolling"
      - "Proxy testing and management CLI"
      - "Integration with free_traffic_launch pipeline"
---