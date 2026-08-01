# Human-Centric Domains — Knowledge Cube Gap Reference

## Discovery (2026-06-11)

Cube содержал 96 доменов, ВСЕ технические. 11 человеко-доменов отсутствовали полностью.
Причина: `config/domain_definitions.yaml` имел только технические домены.
auto_tagger не мог классифицировать то, чего нет в definitions.

## The Fix

Добавлены 11 человеко-доменов в domain_definitions.yaml, затем:
1. `python scripts/auto_tagger.py --force` — переклассифицировал 136 записей
2. white_spot_clusters — 11 новых white spots зарегистрированы
3. Пустые домены — требуют посева

## Номенклатура доменов

### social-media
Социальные сети, мессенджеры, публичные коммуникации
- keywords: twitter, x, telegram, discord, "social media", "social network", messaging, channel, пост, твит, message, dm, follower, subscriber, audience, engagement, platform, тг, tg, community, group, чат, chat, канал
- tag mentions in cube: ~1393
- initial entries after reclassify: 40

### finance
Финансы, инвестиции, криптовалюты, платежи
- keywords: finance, financial, stock, crypto, bitcoin, ethereum, invest, investment, trading, trade, money, payment, price, market, portfolio, asset, доход, прибыль, budget, cost, fee, revenue, earning, fund, polymarket, "prediction market"
- existing skills: stocks, excel-author, pptx-author, earning-with-ai, polymarket
- initial entries: 13

### health-fitness
Здоровье, фитнес, питание, тренировки
- keywords: health, fitness, gym, workout, exercise, nutrition, diet, тренировка, спорт, здоровье, protein, weight, muscle, calories, meal, food, supplement, running, cardio
- existing skills: fitness-nutrition
- initial entries: 3

### entertainment
Игры, развлечения, хобби, досуг
- keywords: game, gaming, pokemon, pokémon, minecraft, игра, entertainment, play, gameplay, server, mod, modpack, emulator, pyboy, gba, nes, snes, arcade, retro, "pixel art"
- exclude: bug, error
- existing skills: pokemon-player, gaming skills
- initial entries: 9

### smart-home
Умный дом, IoT, автоматизация жилья
- keywords: hue, "philips hue", light, "smart home", iot, automation, sensor, "умный дом", thermostat, switch, scene, "voice control", alexa, "home assistant", openhue
- existing skills: openhue
- initial entries: 2

### business-marketing
Бизнес, маркетинг, SEO, монетизация
- keywords: business, marketing, seo, monetize, monetization, revenue, audience, growth, strategy, бизнес, маркетинг, продажи, customer, клиент, lead, funnel, conversion, campaign, advertising, brand, "market research"
- existing skills: earning-with-ai
- initial entries: 0 (пустой — требует посева!)

### music-audio
Музыка, аудио, подкасты, звук
- keywords: music, audio, song, album, spotify, podcast, sound, beat, melody, lyrics, музыка, трек, spectrogram, soundcloud, suno, heartmula, generation, musicgen
- existing skills: spotify, songwriting, heartmula, songsee
- initial entries: 19

### video-content
Видео, YouTube, контент-креация
- keywords: youtube, video, content, upload, stream, streaming, "ascii video", ютуб, видео, канал, creator, subscriber, edit, production, tutorial, vlog
- existing skills: youtube-content, ascii-video
- initial entries: 9

### education
Обучение, академические знания, исследования
- keywords: study, learn, course, tutorial, academic, paper, research, arxiv, science, university, обучение, курс, лекция, education, teach, lesson, class, учебник, exam, degree, "knowledge base", wiki
- exclude: bug, error, fix
- initial entries: 11

### lifestyle
Образ жизни, привычки, организация, заметки
- keywords: lifestyle, habit, routine, note, journal, diary, reminder, todo, task, список, plan, schedule, calendar, apple, macos, ios, iphone, ipad, reminder, "notes app", obsidian
- existing skills: obsidian, apple skills
- initial entries: 12

### productivity
Инструменты продуктивности, управление проектами
- keywords: productivity, notion, linear, airtable, todoist, "project management", kanban, board, task, workflow, asana, trello, agile, sprint, planning, organization, calendar, gmail, "google workspace", drive, docs, sheets
- exclude: bug, error, fix
- existing skills: notion, linear, airtable, google-workspace, project-planner
- initial entries: 16

## Процедура: добавить новый человеко-домен

```bash
# 1. Добавить в config/domain_definitions.yaml
# 2. Переклассифицировать
python scripts/auto_tagger.py --force

# 3. Проверить результат
python -c "
import sqlite3
db = sqlite3.connect('cache/knowledge_cube.db')
c = db.cursor()
c.execute('SELECT axis_domain, COUNT(*) FROM experiences GROUP BY axis_domain ORDER BY COUNT(*) DESC')
for r in c.fetchall():
    print(f'{r[0]:<30} {r[1]}')
"

# 4. Зарегистрировать white spot
python -c "
import sqlite3, uuid
db = sqlite3.connect('cache/knowledge_cube.db')
c = db.cursor()
c.execute('''
    INSERT OR IGNORE INTO white_spot_clusters
    (cluster_id, formed_at, size, representative_text, proposed_dimension, status)
    VALUES (?, datetime(\"now\"), ?, ?, ?, ?)
''', ('human-domain-NEWNAME', 0, 'new human domain', 'NEWNAME', 'developing'))
db.commit()
"

# 5. Если пусто — посеять из существующих навыков/tags
python -c "
import sqlite3
db = sqlite3.connect('cache/knowledge_cube.db')
c = db.cursor()
c.execute('''
    SELECT id, raw_text FROM experiences
    WHERE tags LIKE '%domain:NEWNAME%' OR tags LIKE '%category:NEWNAME%'
    LIMIT 5
''')
for r in c.fetchall():
    print(f'Found: id={r[0]}, text={r[1][:100]}...')
"
```

## Принцип

**Всему нужна категория. Нет категории = white spot = создать ящик и наполнить.**
Не забивать на новую информацию без категории — создать домен, классифицировать, наполнять.
