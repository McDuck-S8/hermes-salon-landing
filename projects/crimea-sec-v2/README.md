# Crimea Security Framework v2 (crimea-sec-v2)

**Легальный пентест / багбаунти / аудит безопасности для Симферополя и Республики Крым**

Адаптация лучших практик из:
- **HexStrike AI** (0x4m4/hexstrike-ai) — MCP-архитектура, 150+ tools, 12 агентов
- **T3MP3ST** (elder-plinius/T3MP3ST) — OPSEC, RoE, Evidence Vault, Mission Control, 8 операторов

---

## 🎯 Цель

Готовый к продакшену фреймворк для **авторизованного** тестирования безопасности:
- Веб-приложения госорганов Крыма (по 152-ФЗ, 187-ФЗ)
- Инфраструктура критического объекта (КИИ) — ГОСТ Р 57580
- Багбаунти-программы: HackerOne, Bugcrowd, Яндекс Багбаунти, Positive Technologies, Solar Dozor
- Коммерческие заказчики (санитары, банки, ритейл, туризм)

---

## 🏗 Архитектура

```
crimea-sec-v2/
├── src/
│   ├── agents/          # 8 операторов (RECON, SCANNER, EXPLOITER*, INFILTRATOR*, EXFILTRATOR*, GHOST*, COORDINATOR, ANALYST)
│   ├── tools/           # Встроенные инструменты (35 built-in + 48 opt-in adapters)
│   ├── arsenal/         # Внешние CLI-тулы (nmap, nuclei, ffuf, sqlmap, amass, subfinder...)
│   ├── opsec/           # OPSEC Layer: 5 пресетов, detection management, cooldowns
│   ├── mission/         # Mission Control: RoE, Kill Chain phases, Task Queue
│   ├── evidence/        # Evidence Vault: findings, credentials, artifacts
│   ├── kb/              # KnowledgeBase: CVE, MITRE ATT&CK, attack patterns
│   ├── mcp/             # MCP Server (stdio + HTTP) для интеграции с Hermes/Claude Code
│   ├── api/             # REST API: /mission/*, /tools/*, /targets/*, /findings/*
│   └── cli/             # CLI: crimea-sec setup|run|report|import|export
├── config/
│   ├── default.yaml     # Базовая конфигурация
│   ├── opsec-profiles.yaml
│   ├── roe-templates.yaml
│   └── crimea-targets.yaml  # Скоупы для Крыма
├── templates/
│   ├── reports/         # HTML/PDF/JSON отчёты
│   ├── scopes/          # Scope receipts templates
│   └── roe/             # Rules of Engagement templates
├── docs/
│   ├── ARCHITECTURE.md
│   ├── OPSEC.md
│   ├── ROE.md
│   ├── LEGAL_RU.md      # 152-ФЗ, 187-ФЗ, ГОСТ Р 57580, УК РФ ст. 272-274
│   └── QUICKSTART.md
├── scripts/
│   ├── install.sh
│   ├── verify-claims.py
│   └── gen-scope-receipt.py
└── tests/
```

> ⚠️ **EXPLOITER, INFILTRATOR, EXFILTRATOR, GHOST, COORDINATOR** помечены `*` — экспериментальные, в продакшене отключены по умолчанию. Используются только RECON, SCANNER, ANALYST.

---

## 🔐 Legal Compliance (Крым / РФ)

| Нормативный акт | Что охватывает | Наш контроль |
|---|---|---|
| **152-ФЗ «О персональных данных»** | Обработка ПДн при тестировании | RoE: scope receipts, data minimization, evidence sanitization |
| **187-ФЗ «О безопасности КИИ»** | Объекты КИИ, категории значимости | Категоризация целей, обязательный Scope Receipt |
| **ГОСТ Р 57580-2017** | Процесс ИБ аудита | Методология аудита в Mission Control |
| **УК РФ ст. 272, 273, 274** | Несанкционированный доступ, вредоносные программы | OPSEC: strict RoE, kill-switch, audit log |
| **ФСТЭК приказ №21** | Защита ГС / КИИ | Только авторизованные сканы, координация с заказчиком |

**Каждый запуск миссии требует:**
1. Подписанный **Scope Receipt** (PDF/JSON) от заказчика
2. Заполненный **RoE** (Rules of Engagement)
3. Активированный **OPSEC preset** (minimum: `balanced`)
4. Включенный **Audit Log** (непрерывный, append-only)

---

## 🚀 Quick Start

```bash
# 1. Установка
cd D:/Portable_Soft/hermes/projects/crimea-sec-v2
./scripts/install.sh

# 2. Конфигурация под Крым
cp config/crimea-targets.yaml.example config/crimea-targets.yaml
# отредактируй scopes, targets, contacts

# 3. Подключение к Hermes (MCP)
# В Hermes: hermes mcp add crimea-sec --command python --args "src/mcp/server.py"

# 4. Запуск миссии (только RECON + SCANNER + ANALYST)
crimea-sec run --target crimea-gov-portal --phase recon,scan,analyze --opsec balanced

# 5. Отчёт
crimea-sec report --mission-id M-2026-001 --format html,pdf
```

---

## 🎯 Целевые объекты Крыма (примеры для config/crimea-targets.yaml)

```yaml
scopes:
  - id: crimea-gov-portal
    name: "Портал госуслуг Республики Крым"
    type: webapp
    urls: ["https://crimea.gov.ru", "https://e-crimea.ru"]
    authorized: true
    contact: "ciso@crimea.gov.ru"
    category: "KII-category-2"
    roe: "strict"

  - id: crimea-tourism
    name: "Туристический портал Крыма"
    type: webapp
    urls: ["https://visitcrimea.ru", "https://krym.travel"]
    authorized: true
    contact: "security@visitcrimea.ru"

  - id: crimea-banks
    name: "Банковская инфраструктура (РНКБ, Крымский фонд и др.)"
    type: network
    cidrs: ["91.200.0.0/16", "185.0.0.0/16"]
    authorized: false  # требует отдельного соглашения
    note: "Требует координации с ФСТЭК и ЦБ РФ"

  - id: crimea-infrastructure
    name: "Критическая инфраструктура (энергори: вода, электричество, транспорт)"
    type: network
    cidrs: ["..."]
    authorized: false
    category: "KII-category-1"
    note: "Только по согласованию с НКЦКИ и ФСТЭК"
```

---

## 🛡 OPSEC Пресеты для Крыма

| Пресет | Использование | Tools | Cooldown |
|---|---|---|---|
| `silent` | Пассивный рекон, OSINT, DNS | amass, subfinder, whois, dnsrecon | 30s |
| `balanced` | Стандартный веб-аудит | nuclei, ffuf, nmap -sS, sslscan | 10s |
| `aggressive` | Полный активный скан (только с RoE=permissive) | nmap -A, sqlmap, nuclei -t cves/ | 5s |
| `apt` | Долгосрочная кампания, low-and-slow | custom scripts, living-off-land | 60s+ |
| `redteam` | Полная цепочка (требует EXPLICIT approval) | all tools, evasion | manual |

---

## 📋 Mission Control — Kill Chain Phases

```yaml
phases:
  - id: recon
    name: "Разведка (TA0043)"
    operators: [RECON]
    tools: [amass, subfinder, dnsrecon, whois, shodan, censys]
    output: "recon-report.json"
    gate: "scope-receipt-verified"

  - id: scan
    name: "Сканирование (TA0007)"
    operators: [SCANNER]
    tools: [nmap, nuclei, ffuf, sslscan, nikto]
    output: "scan-results.json"
    gate: "recon-complete"

  - id: analyze
    name: "Анализ и отчёт (TA0009)"
    operators: [ANALYST]
    tools: [kb-query, cvss-calc, mitre-map]
    output: "final-report.html"
    gate: "scan-complete"

  # ЭКСПЕРИМЕНТАЛЬНЫЕ — отключены по умолчанию:
  - id: exploit
    name: "Эксплуатация (TA0001)"
    operators: [EXPLOITER*]
    status: "experimental"
    requires_explicit_approval: true

  - id: post-exploit
    name: "Пост-эксплуатация (TA0008)"
    operators: [INFILTRATOR*, EXFILTRATOR*, GHOST*]
    status: "experimental"
    requires_explicit_approval: true
```

---

## 📦 Evidence Vault — Структура находки

```json
{
  "finding_id": "FND-2026-001234",
  "mission_id": "M-2026-001",
  "phase": "scan",
  "operator": "SCANNER",
  "target": "https://crimea.gov.ru",
  "vulnerability": {
    "cve": "CVE-2024-12345",
    "cwe": "CWE-79",
    "title": "Reflected XSS in search parameter",
    "cvss31": "6.1 (AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)",
    "mitre": ["T1190", "T1059.007"]
  },
  "evidence": {
    "request": "GET /search?q=<script>alert(1)</script>",
    "response": "<script>alert(1)</script> reflected in body",
    "screenshot": "evidence/FND-2026-001234.png",
    "curl_command": "curl -X GET 'https://crimea.gov.ru/search?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E'"
  },
  "severity": "MEDIUM",
  "status": "verified",
  "remediation": "Implement CSP, encode output, validate input",
  "references": ["https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-12345"]
}
```

---

## 🔌 MCP Integration (Hermes / Claude Code)

```json
// ~/.hermes/mcp.json или claude_desktop_config.json
{
  "mcpServers": {
    "crimea-sec": {
      "command": "python",
      "args": ["D:/Portable_Soft/hermes/projects/crimea-sec-v2/src/mcp/server.py"],
      "env": {
        "CRIMEA_SEC_CONFIG": "D:/Portable_Soft/hermes/projects/crimea-sec-v2/config/default.yaml",
        "T3MP3ST_FULL_ARSENAL": "false"
      }
    }
  }
}
```

Доступные MCP tools:
- `security_recon` — пассивная разведка (DNS, subdomain, WHOIS, cert transparency)
- `security_scan` — активное сканирование (nmap, nuclei, ffuf)
- `security_analyze` — анализ находок, CVSS, MITRE mapping
- `mission_start` — запуск миссии по RoE
- `mission_status` — статус выполнения
- `evidence_get` — получение доказательств
- `report_generate` — генерация отчёта

---

## ✅ Verification Gates (verify-claims)

```bash
# Проверка что всё работает и каталог инструментов честен
python scripts/verify-claims.py

# Ожидаемый вывод:
# ✅ 35 built-in tools wired
# ✅ 48 opt-in adapters catalogged
# ✅ 8 operators defined (3 stable, 5 experimental)
# ✅ OPSEC presets: 5
# ✅ RoE templates: 3
# ✅ KnowledgeBase: 20 CVEs, 40+ MITRE techniques
# ✅ MCP server: stdio + HTTP
# ⚠️ EXPLOITER/INFILTRATOR/EXFILTRATOR/GHOST/COORDINATOR = experimental
```

---

## 📚 Документация

- [Архитектура](docs/ARCHITECTURE.md)
- [OPSEC Guide](docs/OPSEC.md)
- [Rules of Engagement](docs/ROE.md)
- [Legal Compliance РФ](docs/LEGAL_RU.md)
- [Quick Start](docs/QUICKSTART.md)
- [Crimea Targets Config](config/crimea-targets.yaml)

---

## ⚖️ Лицензия

**AGPL-3.0** — как T3MP3ST. Любое коммерческое использование требует открытия кода.
Для проприетарного использования — свяжитесь с автором для коммерческой лицензии.

---

## ⚠️ Disclaimer

> **Только для авторизованного тестирования.**
> Направляйте инструменты ТОЛЬКО на системы, которыми вы владеете или имеете **письменное разрешение** на тестирование.
> Несанкционированный доступ к компьютерной информации — преступление (УК РФ ст. 272, 273, 274).
> Авторы не несут ответственности за неправомерное использование.