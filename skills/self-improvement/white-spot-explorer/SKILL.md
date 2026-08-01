---
name: white-spot-explorer
description: "Исследует белые пятна Knowledge Cube через opencode.ai/zen/v1 (deepseek-v4-flash-free). Событийный запуск — не по расписанию."
version: 2.2.0
author: Hermes
metadata:
  hermes:
    tags: [knowledge-cube, self-improvement, white-spots, qwen, deepseek]
    trigger: manual | event (новое белое пятно в Cube)
---

# White Spot Explorer

## Когда использовать

Когда в Knowledge Cube есть:
- Домены с <10 записей (традиционные белые пятна)
- **Домены, которые ДОЛЖНЫ существовать, но НЕ СУЩЕСТВУЮТ** (критическое расширение — см. Phase 0)

Запускается вручную или по событию. НЕ по расписанию.

## Фундаментальный принцип

**«Новая информация без категории = white spot = создать ящик и наполнить»**
— user correction, 2026-06-11

Всему нужно присваивать категорию. Если данных по теме нет — это не значит, что темы не существует. Это значит, что категория не создана. Создай → классифицируй → наполни.

## Порядок работы

### Phase 0: Детекция MISSING доменов (ВАЖНЕЙШЕЕ РАСШИРЕНИЕ)

Не смотри только на то, что ЕСТЬ в cube. Смотри на то, что ДОЛЖНО БЫТЬ, но отсутствует.

#### Шаг 0.1: Собрать источники существующих тем

```
1. config/domain_definitions.yaml — какие домены определены
2. tags в Knowledge Cube — какие domain:XXX теги есть в записях
3. skills_list — какие навыки установлены
4. Из истории разговоров — о чём пользователь говорит
```

#### Шаг 0.2: Сравнить с axis_domain в Cube

#### Шаг 0.3: Человеко-домены (критически важны)

Технических доменов в cube достаточно (bugfix, coding, file_ops, devops и т.д.).
**Человеко-домены полностью отсутствуют**, если их не добавить явно:

| Домен | Примеры тем |
|-------|------------|
| social-media | Telegram, Twitter/X, соцсети, мессенджеры |
| finance | Акции, крипта, инвестиции, платежи |
| health-fitness | Фитнес, питание, тренировки, здоровье |
| entertainment | Игры, Pokemon, Minecraft |
| music-audio | Spotify, Suno, музыка, аудио |
| video-content | YouTube, видео, контент |
| education | Курсы, paper, arxiv, обучение |
| lifestyle | Заметки, reminders, организация |
| productivity | Notion, Linear, Airtable |
| smart-home | Philips Hue, IoT |
| business-marketing | SEO, маркетинг, монетизация |

**Алгоритм:** Если пользователь упоминает тему, а в cube нет домена — ЭТО БЕЛОЕ ПЯТНО. Создай домен → зарегистрируй white spot → классифицируй существующие записи → сей новые.

#### Шаг 0.4: Рабочий процесс (ВАЛИДИРОВАН 2026-07-04)

```bash
# 1. Добавить домен в config/domain_definitions.yaml (если отсутствует)
# 2. Переклассифицировать автотеггером
python scripts/auto_tagger.py --force
# 3. Проверить распределение
python -c "
import sqlite3
db = sqlite3.connect('cache/knowledge_cube.db')
c = db.cursor()
c.execute('SELECT axis_domain, COUNT(*) FROM experiences GROUP BY axis_domain ORDER BY COUNT(*) DESC')
for r in c.fetchall():
    print(f'{r[0]:<30} {r[1]}')
"

# 4. Зарегистрировать как white spot в white_spot_clusters
INSERT INTO white_spot_clusters (cluster_id, formed_at, size, representative_text, proposed_dimension, status)
VALUES ('human-domain-{name}', datetime('now'), {cnt}, '{desc}', '{name}', 'developing');

# 5. Если домен пуст (0 записей) — посеять начальное знание из навыков/tags
# (Skill name -> domain mapping: telegram-bot-integration -> social-media, stocks -> finance, etc.)
```

**КРИТИЧЕСКИ ВАЖНО (POLICY 20):** Никогда не спрашивай "хочешь запустить?". Запусти auto_tagger --force, посей, зарегистрируй. Доложи фактом.

```python
import sqlite3, json

db = sqlite3.connect('cache/knowledge_cube.db')
c = db.cursor()

# Что есть в axis_domain
c.execute("SELECT DISTINCT axis_domain FROM experiences WHERE axis_domain != ''")
existing = set(r[0] for r in c.fetchall())

# Что есть в tags (domain:XXX)
c.execute("SELECT tags FROM experiences WHERE tags IS NOT NULL")
tag_domains = set()
for r in c.fetchall():
    try:
        tags = json.loads(r[0]) if isinstance(r[0], str) else [r[0]]
        for tag in tags if isinstance(tags, list) else [tags]:
            ts = str(tag).strip()
            if ts.startswith('domain:'):
                bare = ts.replace('domain:', '')
                if bare not in existing:
                    tag_domains.add((bare, ts))
    except: pass

# Что есть в skill_index
c.execute("SELECT category FROM skill_index")
skill_cats = set()
for r in c.fetchall():
    cat = r[0]
    if cat and cat not in existing:
        skill_cats.add(cat)

print("MISSING domains (in tags but not axis_domain):")
for dom in sorted(tag_domains):
    print(f"  {dom}")

print("MISSING domains (skill categories not in cube):")
for cat in sorted(skill_cats):
    print(f"  {cat}")
```

#### Шаг 0.3: Человеко-домены (критически важны)

Технических доменов в cube достаточно (bugfix, coding, file_ops, devops и т.д.).
**Человеко-домены полностью отсутствуют**, если их не добавить явно:

| Домен | Примеры тем |
|-------|------------|
| social-media | Telegram, Twitter/X, соцсети, мессенджеры |
| finance | Акции, крипта, инвестиции, платежи |
| health-fitness | Фитнес, питание, тренировки, здоровье |
| entertainment | Игры, Pokemon, Minecraft |
| music-audio | Spotify, Suno, музыка, аудио |
| video-content | YouTube, видео, контент |
| education | Курсы, paper, arxiv, обучение |
| lifestyle | Заметки, reminders, организация |
| productivity | Notion, Linear, Airtable |
| smart-home | Philips Hue, IoT |
| business-marketing | SEO, маркетинг, монетизация |

**Алгоритм:** Если пользователь упоминает тему, а в cube нет домена — ЭТО БЕЛОЕ ПЯТНО. Создай домен → зарегистрируй white spot → классифицируй существующие записи → сей новые.

#### Шаг 0.4: Рабочий процесс

```
1. Добавить домен в config/domain_definitions.yaml
   — описание на русском/английском
   — keywords (ключевые слова на EN + RU)
   — exclude_keywords при необходимости

2. Запустить auto_tagger --force
   python scripts/auto_tagger.py --force
   → переклассифицирует существующие записи в новый домен

3. Проверить распределение
   SELECT axis_domain, COUNT(*) FROM experiences GROUP BY axis_domain;

4. Зарегистрировать как white spot в white_spot_clusters
   INSERT INTO white_spot_clusters 
   (cluster_id, formed_at, size, representative_text, proposed_dimension, status)
   VALUES ('human-domain-{name}', datetime('now'), {cnt}, '{desc}', '{name}', 'developing');

5. Если домен пуст (0 записей) — посеять начальное знание
   — из skill_index: найти связанные навыки
   — из conversations: найти упоминания в state.db
   — из tags: найти записи с domain:XXX в tags
```

### Phase 0.5: Multi-table uncategorized audit (2026-07-19)

Перед сканированием белых пятен — проверить **обе** таблицы Cube на uncategorized записи.
`auto_tagger` и ingestion pipelines не всегда синхронизируют `tags` → `axis_domain`.

```sql
-- 1. experiences table: check total uncategorized
SELECT COUNT(*) as uncat_count
FROM experiences 
WHERE axis_domain IS NULL OR axis_domain = '' OR axis_domain = 'uncategorized';

-- 2. kc_entries table: separate schema, separate category column
SELECT COUNT(*) as uncat_count
FROM kc_entries 
WHERE category IS NULL OR category = '' OR category = 'uncategorized';

-- 3. DETECT TAG/AXIS_DOMAIN MISMATCH (2026-07-19 finding)
-- Entries with domain:XXX in tags but empty axis_domain = sync bug
SELECT id, tags 
FROM experiences 
WHERE (axis_domain IS NULL OR axis_domain = '' OR axis_domain = 'uncategorized')
  AND tags LIKE '%domain:%'
  AND tags NOT LIKE '%rejected-by-user%';
```

**Обнаруженная проблема (2026-07-19):** 25 entries had `tags=["domain:coding",...]` but empty `axis_domain`.
Фикс:
```sql
UPDATE experiences 
SET axis_domain = SUBSTR(tags, INSTR(tags, 'domain:') + 7, 
                          INSTR(SUBSTR(tags, INSTR(tags, 'domain:') + 7), '"') - 1)
WHERE (axis_domain IS NULL OR axis_domain = '' OR axis_domain = 'uncategorized')
  AND tags LIKE '%domain:%'
  AND tags NOT LIKE '%rejected-by-user%';
```

### Phase 1: Получить белые пятна из Knowledge Cube

После Phase 0.5 (multi-table audit), собрать underpopulated домены:

```python
import sys
sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")
import knowledge_cube as kc

db = kc.get_db()
cur = db.execute('''
    SELECT axis_domain, COUNT(*) as cnt
    FROM experiences
    GROUP BY axis_domain
    HAVING cnt < 10
    ORDER BY cnt
''')
white_spots = {r['axis_domain']: r['cnt'] for r in cur.fetchall()}
print(f"Белые пятна: {white_spots}")
```

### Phase 2: Выбрать цель для исследования

Приоритет:
1. MISSING домены (из Phase 0) — их нет вообще
2. Домены с 0 записей (созданы, но пусты)
3. Домены с <5 записей
4. Домены с <10 записей

### 3. Исследовать через LLM (opencode.ai/zen/v1)

Использовать opencode.ai/zen/v1 (deepseek-v4-flash-free) для анализа доменов.
API доступен через `direct_api` модуль в `plugins/self-evolution/evolution/core/direct_api.py`.

**ВАЖНО — защита от перегрузки:**
- Не слать больше 1 запроса в 3-5 секунд
- При ошибке — пауза 10+ секунд перед ретраем
- Макс 5 запросов на домен — не спамить

**Через direct_api (рекомендуемый способ):**
```python
import sys
sys.path.insert(0, "D:/Portable_Soft/hermes/plugins/self-evolution")
from evolution.core.direct_api import direct_generate

prompt = f"Проанализируй эти записи из домена '{domain}' и выдели ключевые концепции, паттерны и связи: {sample_texts}"
result = direct_generate(prompt, max_tokens=2000)
```

**Если direct_api недоступен — через curl (OpenAI-совместимый):**
```bash
curl -s https://opencode.ai/zen/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENCODE_ZEN_API_KEY" \
  -d '{
    "model": "deepseek-v4-flash-free",
    "messages": [{"role": "user", "content": "..."}],
    "max_tokens": 2000
  }'
```

### 4. Обработать результат

Из ответа LLM извлечь:
- Ключевые концепции домена
- Паттерны и связи с другими доменами
- Готовые записи для Knowledge Cube

Записать в Cube через event_evolution:
```python
from scripts.event_evolution import on_task_complete
on_task_complete(
    content="Исследован домен X: найденные концепции...",
    tags=["domain:X", "white-spot", "exploration"],
    source="white-spot-explorer"
)
```

### 5. Создать навык если найдены устойчивые паттерны

Если в домене найдено >5 связанных концепций — создать навык через skill_manage.

## КРИТИЧЕСКИЙ ПИТФОЛ — НЕ ИСПОЛЬЗОВАТЬ delegate_task

**delegate_task блокирует родительскую сессию.** Пользователь видит 7+ минут тишины.
Это системный долг, который раздражает пользователя.

**Для white-spot-explorer используйте execute_code напрямую:**
```python
from hermes_tools import terminal
import json, time

# Шаг 1 — генерируем концепции через DeepSeek
print("1/3: Генерация концепций через DeepSeek...")
result = terminal("""curl -s http://localhost:9655/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"..."}],"max_tokens":1000}'
""")
# Отписываемся сразу
# ... (остальные шаги)
```

**Почему:** 6 запросов к API через execute_code = ~2 минуты.
Тот же объём через delegate_task = 7 минут (накладные расходы на контекст агента).

**Когда delegate_task оправдан:** задача требует изолированного контекста (кодинг, отладка, многомодульный анализ). Для простых API-вызовов — нет.

---

### Practical Learnings (2026-07-05 session)

#### LLM Provider: localhost:9655 (DeepSeek) vs opencode.ai/zen
- **opencode.ai/zen** requires API key, returns 401 without it
- **localhost:9655** runs DeepSeek-V4-Flash (free, no auth, web search optional)
- Models available: `deepseek-chat`, `deepseek-reasoner`, `deepseek-chat-search`, etc.
- Use `curl` or `urllib` directly from `execute_code` — no auth needed

#### Rate Limiting & Reliability
- DeepSeek on localhost:9655 handles ~1 req/3-5 sec comfortably
- Add `time.sleep(3)` between requests
- On 429/5xx: back off 30 sec, then retry
- Max 5 requests per domain per session (cost control)

#### Schema Fix: experiences table
- Column is `confidence` (REAL), NOT `axis_confidence`
- Column is `ts` (TEXT), NOT `timestamp`
- Use `hash` (TEXT) for deduplication (md5 of content)
- `dynamic_axes` stores JSON: `{"topic": "arbitrage", "research": true}`
- **Full INSERT columns**: `content, raw_text, source, confidence, ts, hash, dynamic_axes, axis_domain, tags, is_white_spot, importance`
- `raw_text` NOT NULL constraint — must duplicate content or provide original

#### White Spot Cluster Updates
```sql
-- After inserting research, update cluster size from actual data
UPDATE white_spot_clusters 
SET size = (SELECT COUNT(*) FROM experiences WHERE axis_domain = proposed_dimension)
WHERE status = "researched";
```

#### Incomplete Cluster Audit (2026-07-19)

После анализа uncategorized записей — проверить `white_spot_clusters` на незавершённые регистрации.
Кластеры со статусом `pending` БЕЗ `proposed_dimension` — это незаконченные предыдущие запуски.

```sql
-- Найти брошенные кластеры
SELECT cluster_id, size, formed_at
FROM white_spot_clusters
WHERE status = 'pending' AND (proposed_dimension IS NULL OR proposed_dimension = '');

-- Закрыть их (назначить dimension или удалить если мусор)
UPDATE white_spot_clusters
SET proposed_dimension = 'unknown-needs-review', status = 'stale'
WHERE status = 'pending' AND (proposed_dimension IS NULL OR proposed_dimension = '');
```

#### Cost Tracking
- All LLM calls logged via `cost_tracker.log_cost(model, input_tokens, output_tokens, ...)`
- DeepSeek-V4-Flash: ~$0.14/1M input, $0.28/1M output (very cheap)
- 9 domains × ~2000 tokens = ~$0.0013 total

#### Token Compression Integration
- Add `auto_compress(messages)` before LLM calls in `call_llm()`
- Saves 40-75% on tool outputs
- Already integrated in `llm_analyst.py` and `autonomous_agent.py`

---

## Practical Learnings (2026-07-06 session) — Batch Domain Research

### Complete 7-Domain Research Workflow (Validated)

This session executed a full batch research of 7 new domains in one run:
1. **advanced-analytics** — Bayesian A/B testing, sequential testing, hierarchical models
2. **behavioral-psychology** — Cognitive biases, neuromarketing, Cialdini/Fogg/Hook frameworks
3. **organic-traffic** — SEO clusters, YouTube/Pinterest SEO, AI content, repurposing 1→10+
4. **crypto-web3** — DeFi primitives, staking/restaking, MEV, cross-chain arb, stablecoin yields
5. **ai-content-factory** — Local SD/Flux/video, ComfyUI, quantization, automation, business models
6. **b2b-sales** — Cold email, SPIN/MEDDIC, demo, pricing, objections (LAER), closing, tools
7. **referral-automation** — Top programs, recurring commissions, packaging turnkey solutions, funnels, K-factor

### Batch Research Pattern (Reusable)

```python
# 1. Add domains to config/domain_definitions.yaml with keywords (EN + RU)
# 2. Register white spot clusters (size=0, status='developing')
# 3. For each domain:
#    a. DeepSeek prompt covering 8 structured subtopics, 2-3 sentences each, Russian
#    b. execute_code with urllib to localhost:9655/v1/chat/completions (model=deepseek-chat)
#    c. time.sleep(3) between requests
#    d. Insert into experiences table with full schema
#    e. Update white_spot_clusters (size=actual count, status='researched')
# 4. Run auto_tagger.py --force to reclassify existing entries
# 5. Verify distribution: SELECT axis_domain, COUNT(*) FROM experiences GROUP BY axis_domain

# Cost: ~7 domains × 2500 tokens = ~17,500 tokens = ~$0.004 (DeepSeek-V4-Flash)
# Time: ~3 min total (7 × 25 sec API + sleeps)
```

### DeepSeek API Integration (execute_code + urllib)

```python
import json, urllib.request, time

def ask_deepseek(prompt, max_tokens=2500):
    url = "http://localhost:9655/v1/chat/completions"
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())["choices"][0]["message"]["content"]

# Usage:
result = ask_deepseek(prompt)
time.sleep(3)  # Rate limit
```

### Schema-Compliant Insert (Critical)

```python
import hashlib, json, sqlite3
from datetime import datetime

content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute("""
    INSERT INTO experiences (content, raw_text, source, confidence, ts, hash, 
                             dynamic_axes, axis_domain, tags, is_white_spot, importance)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    content, content, "white-spot-explorer", 0.95, datetime.now().isoformat(), content_hash,
    json.dumps({"topic": domain, "research": True, "white_spot": True}),
    domain,
    json.dumps([domain, "white-spot", "research", *subtags]),
    1, 0.9
))
```

### Auto-Tagger Reclassification Step

After inserting new domain research, **always run**:
```bash
python scripts/auto_tagger.py --force
```
This reclassifies existing entries using the new domain keywords (442 reclassified in this session). Without this, the new domains only have the manually inserted research entries.

---

### 2026-07-05 Session Results

**Researched 9/11 human domains:**
| Domain | Entries | Status |
|--------|---------|--------|
| smart-home | 6 | ✅ researched |
| lifestyle | 6 | ✅ researched |
| entertainment | 6 | ✅ researched |
| health-fitness | 10 | ✅ researched |
| business-marketing | 10 | ✅ researched |
| education | 11 | ✅ researched |
| music-audio | 12 | ✅ researched |
| video-content | 12 | ✅ researched |
| finance | 4 | ⏳ pending (HITL) |

**Tokens used:** ~18,000 tokens → **$0.0013** (DeepSeek-V4-Flash via localhost:9655)

**Next actions:**
1. HITL approval for finance domain (waiting for user)
2. Productivity (13 entries, developing) — needs research
3. Social-media (17 entries, developing) — needs research

## Промежуточная отписка (responsiveness pattern)

После каждого завершённого шага давать статус:
```
"1/3: Концепции получены (6 шт.)"
"2/3: Расширение через LLM готово"
"3/3: Записано в Cube"
```

Это решает проблему "тишины". Пользователь видит прогресс.

## Lessons Learned (2026-07-06 Session — Second Course)

### Critical Correction: Quantity IS a Criterion
**User correction:** "Количество — это тоже критерий. Одна длинная статья не равна пяти разным заметкам с разных углов."
- Minimum **5 entries per domain** in Knowledge Cube
- Each entry = different angle, different source, different subtopic
- NOT "one comprehensive article = 5 entries"

### Working Pattern: Batch Domain Research (Validated 2026-07-06)

```python
# Phase 1: Add domains to domain_definitions.yaml (EN/RU keywords)
# Phase 2: auto_tagger --force (reclassify existing entries)
# Phase 3: Register white_spot_clusters with size=0, status='developing'
# Phase 4: For each domain, research 5 subtopics via DeepSeek (localhost:9655)
# Phase 5: Insert each as separate experience with unique hash
# Phase 6: Update white_spot_clusters size=5, status='researched'
```

**Performance:** 7 domains × 5 entries = 35 records in ~2.5 hrs, ~$0.015 on DeepSeek-V4-Flash (localhost:9655)

### Tool Choice: execute_code > delegate_task for White Spot Explorer
- delegate_task blocks parent session 7+ min (context overhead)
- execute_code with direct curl to localhost:9655 = ~2 min per domain batch
- Rate limit: 3-5 sec between requests, max 5 requests/domain/session

### GitHub Project Analysis Patterns (Ada-SI, Mark-XLVIII)
When analyzing similar agent architectures, extract:
| Pattern | Ada-SI | Mark-XLVIII | Hermes Application |
|---------|--------|-------------|-------------------|
| **Multi-service** | Chat(8080) + LiteLLM(4000) + ToolRuntime(8090) | main.py + actions/ + ui.py | Consider: separate tool runtime service |
| **Dynamic tool creation** | Forge system (generate_new_tool, edit_existing_tool) | — | Our procedural_executor could adopt plan→approve→execute |
| **Real-time voice** | — | Gemini Live API, 50ms audio chunks, instant interrupt | Voice interface skill needs audio streaming |
| **Vision** | — | Screen capture → Gemini Live, immediate ack | Our agent-browser needs real-time screen feed |
| **Memory** | localStorage + staging/ + custom_tools/ | Persistent KV across sessions | Our KC + state.db + memories/ |
| **Proactive** | Heartbeat supervisor → LLM calls on timer | 15-min silence check-ins (Gemini-decided) | Our event_daemon + proactive_engine |
| **Zero terminal** | subprocess CREATE_NO_WINDOW | Subprocess monkey-patch | Apply to all background scripts |

### Recommended Hermes Upgrades from Analysis
1. **Tool Runtime Service** — isolate tool execution (security, like Ada-SI's port 8090)
2. **Forge/Plan-Approval System** — dynamic tool creation with human-in-the-loop (Ada-SI pattern)
3. **Voice Streaming** — Gemini Live API integration (Mark-XLVIII pattern)
4. **Real-time Vision** — screen capture → LLM with immediate acknowledgment
5. **Proactive Check-ins** — LLM-decided, not hardcoded (Mark-XLVIII: "Gemini decides, no hardcoded rules")
6. **Parallel Operations** — concurrent startup phases, parallel search backends

## Reusable script
## Working recipe: Seed empty human domains (validated 2026-07-04)

After Phase 0 detects missing human domains (via `human-domain-gap-analysis`), white-spot-explorer can seed them:

### 1. Ensure domains exist in domain_definitions.yaml
```yaml
# All 11 human domains must be present:
social-media, finance, health-fitness, entertainment, smart-home,
business-marketing, music-audio, video-content, education, lifestyle, productivity
```

### 2. Reclassify with auto_tagger
```bash
python scripts/auto_tagger.py --force
# 1371/1522 entries reclassified in ~2 seconds
```

### 3. Seed from skill index
```python
skill_to_domain = {
    'stocks': 'finance', 'excel-author': 'finance', 'pptx-author': 'finance',
    'earning-with-ai': 'business-marketing', 'polymarket': 'finance',
    'fitness-nutrition': 'health-fitness', 'pokemon-player': 'entertainment',
    'openhue': 'smart-home', 'spotify': 'music-audio', 'heartmula': 'music-audio',
    'songsee': 'music-audio', 'youtube-content': 'video-content', 'ascii-video': 'video-content',
    'arxiv': 'education', 'llm-wiki': 'education', 'obsidian': 'lifestyle',
    'notion': 'productivity', 'linear': 'productivity', 'airtable': 'productivity',
    'google-workspace': 'productivity', 'project-planner': 'productivity',
    'telegram-bot-integration': 'social-media', 'telegram-service-bot': 'social-media',
    'agent-browser': 'social-media',
}
# For each skill → domain: INSERT into experiences (axis_domain=domain, tags=['skill','domain:X','seeded'])
```

### 4. Register white spot clusters with correct size/status
```sql
INSERT OR IGNORE INTO white_spot_clusters
(cluster_id, formed_at, size, representative_text, proposed_dimension, status)
VALUES 
('human-domain-finance', now(), 4, 'Seeded human domain: finance', 'finance', 'developing'),
('human-domain-productivity', now(), 5, 'Seeded human domain: productivity', 'productivity', 'developing'),
('human-domain-social-media', now(), 9, 'Seeded human domain: social-media', 'social-media', 'developing'),
-- ... etc for all 11
```

### 5. Verify results
```bash
python -c "
import sqlite3
db = sqlite3.connect('cache/knowledge_cube.db')
c = db.cursor()
c.execute('SELECT axis_domain, COUNT(*) FROM experiences GROUP BY axis_domain ORDER BY COUNT(*) DESC')
for r in c.fetchall(): print(f'{r[0]:<25} {r[1]}')
"
```
Expected: all 11 human domains visible with counts >0.

### 6. Next white-spot-explorer run
- Will pick up `developing` clusters (size > 0)
- Use opencode.ai/zen to expand with real knowledge (traffic sources, monetization, formats)
- Replace seed entries with rich domain knowledge
См. `references/human-domains.md` — 11 человеко-доменов, номенклатура, ключевые слова, процедура добавления.
См. `references/2026-07-04-session-findings.md` — находки текущей сессии: 17 пустых доменов, пустая white_spot_clusters, план действий, 24 концепции добавлены.

## Reusable script

После первого запуска создан `scripts/explore_design_domain.py` (228 строк). Можно использовать как шаблон для других доменов: заменить название домена и промпт.

См. `references/run-recipe.md` с полным рецептом и pitfall-ами.
См. `references/human-domains.md` — 11 человеко-доменов, номенклатура, ключевые слова, процедура добавления.

## Working recipe: Seed empty human domains (validated 2026-07-04)

After Phase 0 detects missing human domains (via `human-domain-gap-analysis`), white-spot-explorer can seed them:

### 1. Ensure domains exist in domain_definitions.yaml
```yaml
# All 11 human domains must be present:
social-media, finance, health-fitness, entertainment, smart-home,
business-marketing, music-audio, video-content, education, lifestyle, productivity
```

### 2. Reclassify with auto_tagger
```bash
python scripts/auto_tagger.py --force
# 1371/1522 entries reclassified in ~2 seconds
```

### 3. Seed from skill index
```python
skill_to_domain = {
    'stocks': 'finance', 'excel-author': 'finance', 'pptx-author': 'finance',
    'earning-with-ai': 'business-marketing', 'polymarket': 'finance',
    'fitness-nutrition': 'health-fitness', 'pokemon-player': 'entertainment',
    'openhue': 'smart-home', 'spotify': 'music-audio', 'heartmula': 'music-audio',
    'songsee': 'music-audio', 'youtube-content': 'video-content', 'ascii-video': 'video-content',
    'arxiv': 'education', 'llm-wiki': 'education', 'obsidian': 'lian': 'lifestyle',
    'notion': 'productivity', 'linear': 'productivity', 'airtable': 'productivity',
    'google-workspace': 'productivity', 'project-planner': 'productivity',
    'telegram-bot-integration': 'social-media', 'telegram-service-bot': 'social-media',
    'agent-browser': 'social-media',
}
# For each skill → domain: INSERT into experiences (axis_domain=domain, tags=['skill','domain:X','seeded'])
```

### 4. Register white spot clusters with correct size/status
```sql
INSERT OR IGNORE INTO white_spot_clusters
(cluster_id, formed_at, size, representative_text, proposed_dimension, status)
VALUES 
('human-domain-finance', now(), 4, 'Seeded human domain: finance', 'finance', 'developing'),
('human-domain-productivity', now(), 5, 'Seeded human domain: productivity', 'productivity', 'developing'),
('human-domain-social-media', now(), 9, 'Seeded human domain: social-media', 'social-media', 'developing'),
-- ... etc for all 11
```

### 5. Verify results
```bash
python -c "
import sqlite3
db = sqlite3.connect('cache/knowledge_cube.db')
c = db.cursor()
c.execute('SELECT axis_domain, COUNT(*) FROM experiences GROUP BY axis_domain ORDER BY COUNT(*) DESC')
for r in c.fetchall(): print(f'{r[0]:<25} {r[1]}')
"
```
Expected: all 11 human domains visible with counts >0.

### 6. Next white-spot-explorer run
- Will pick up `developing` clusters (size > 0)
- Use opencode.ai/zen to expand with real knowledge (traffic sources, monetization, formats)
- Replace seed entries with rich domain knowledge
См. `references/human-domains.md` — 11 человеко-доменов, номенклатура, ключевые слова, процедура добавления.
См. `references/2026-07-04-session-findings.md` — находки текущей сессии: 17 пустых доменов, пустая white_spot_clusters, план действий, 24 концепции добавлены.

---

### Gap-Patch Workflow (2026-07-14) — Post-Exploration Cleanup

После того как белые пятна исследованы, их нужно **классифицировать и почистить**. Это gap-patch.

#### Gap-Patch Classification (user correction: "не всё непроверенное — мусор")

Не удаляй всё подряд. Сортируй:

| Категория | Действие | Примеры |
|-----------|----------|---------|
| **МУСОР** | Удалить | Нет source, >60 дней, никогда не верифицированы, дубликаты, auto-generated placeholders |
| **ГИПОТЕЗЫ** | Оставить с пониженным confidence | Есть source, но нет верификации. Добавить `#requires-action`. confidence ↓ 0.2-0.3 |
| **НА ПРОВЕРКУ СЕЙЧАС** | Проверить немедленно | Истекла verification_date, блокирует другие знания |

#### White Spot Triage (Session 2026-07-14)

При анализе 105 белых пятен используется классификация:

| Тип | Кол-во | Что делать |
|-----|--------|-----------|
| **knowledge domains** | ~47 | Спросить пользователя: интересна ли тема? Если да — развернуть в план. Если нет — понизить confidence. |
| **session dumps** | ~41 | Ничего. Технические записи. |
| **auto-seeded concepts** | ~11 | Удалить (= auto-generated placeholder ideas, confidence 0.5). |
| **skill→domain mappings** | ~5 | Повысить confidence до 1.0 (тривиально верно). |
| **human domain analysis** | ~1 | Спросить пользователя. |

#### Research Verification Hierarchy

При закрытии пробелов используй **иерархию методов верификации**:

```
official_docs (official docs/source) > cross_referenced (2+ sources) > direct_check (manual check) > manual (speculative)
```

Устанавливай `verification_method` в эту шкалу. Назначай confidence соответственно: 1.0 для official_docs, 0.95 для cross_referenced, 0.95 для direct_check, 0.3 для manual.

#### Handling Rejected Knowledge

Когда пользователь отклоняет целый класс знаний (например, CPA-схемы):

1. Понизить confidence до 0.3
2. Добавить тег `#rejected-by-user`
3. Понизить importance до 0.3
4. НЕ удалять — это гипотезы, не мусор
5. Исключить из future gap-patch и предложений

```sql
UPDATE experiences 
SET confidence = 0.3, importance = 0.3,
    tags = json_set(
      CASE WHEN tags IS NULL OR tags = '' THEN '[]' ELSE tags END,
      '$[#]', 'rejected-by-user'
    )
WHERE <conditions matching rejected class>;
```

#### DB Schema Alert (2026-07-14)

**tags column stores malformed JSON in some records.** Records from auto_tagged sessions have `, auto_tagged, auto_tagged` appended after the JSON array, making `json_set()` fail. Before any JSON operation, normalize:

```sql
UPDATE experiences SET tags = substr(tags, 1, instr(tags, '],') + 1) WHERE tags LIKE '%], auto_tagged%';
```

#### Reporting Requirement

User requires **numbers-first reporting**. Every gap-patch report must include:

```
| Метрика | До | После | Δ |
|---------|-----|-------|---|
|<total records> | X | Y | +Z |
|<avg confidence> | X | Y | +Z |
|<white spots> | X | Y | +Z |
|<#rejected-by-user> | X | Y | +Z |
```

Lead with the table, then explain methodology.

---

## PITFALLS

### Tag/axis_domain mismatch (2026-07-19)

`auto_tagger --force` и ingestion pipelines могут проставить `domain:XXX` в поле `tags`, но **не синхронизировать** поле `axis_domain`. В результате entries выглядят как uncategorized (пустой axis_domain), хотя уже имеют домен в tags.

**Симптом:** SELECT на uncategorized возвращает entries, которые в tags содержат `domain:coding` или аналоги.
**Фикс:** UPDATE с парсингом domain: из tags в axis_domain (см. Phase 0.5).

### Не проверять kc_entries таблицу

`kc_entries` — отдельная таблица с `category` как аналогом `axis_domain`. В ней тоже могут быть uncategorized записи, не учтённые в `experiences`. Всегда проверяй обе таблицы.

### Пропущенные pending кластеры

`white_spot_clusters` может содержать брошенные кластеры от предыдущих запусков (status=pending, proposed_dimension=NULL). Их нужно или закрыть, или назначить dimension. Если не сделать — они копятся.

## Ограничения

- **Никакого расписания** — только ручной запуск или событие
- **1 домен за раз** — не перегружать прокси
- **Пауза между запросами** — 3-5 секунд минимум
- **При ошибке 429/403** — стоп на 30 секунд
- **Макс 5 запросов на домен** — не спамить
- **НЕ ИСПОЛЬЗОВАТЬ delegate_task** — execute_code с прямыми API вызовами

## Проверка

После исследования проверить:
1. Новые записи появились в Knowledge Cube
2. Домен вышел из белых пятен (>10 записей)
3. Если создан навык — он корректен и загружается
