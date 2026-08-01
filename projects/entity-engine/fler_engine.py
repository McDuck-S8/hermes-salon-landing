#!/usr/bin/env python3
"""
Fler Engine — детектор флра (атмосферы) разговоров.

Три сущности:
  ФЛЁР — атмосфера, которая окружает взаимодействие
  ПОСЛЕВКУСИЕ — остаточный эффект после сессии
  ЗАГРЯЗНЕНИЕ — негативный контекст, который заражает флёр

Использование:
  python fler_engine.py demo          — демо-анализ на примерах
  python fler_engine.py analyze FILE  — анализ файла с диалогом
  python fler_engine.py stats         — статистика по всем сессиям
"""

import re, json, os, sys, sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))) / "cache" / "fler_engine.db"


# ============ LEXICONS ============

POSITIVE_WORDS = {
    "ru": {"хорошо", "отлично", "супер", "круто", "молодец", "спасибо", "пожалуйста",
           "рад", "доволен", "класс", "прекрасно", "замечательно", "идеально", "браво",
           "согласен", "точно", "именно", "верно", "правильно", "да", "конечно",
           "получилось", "готово", "сделано", "работает", "жив", "ура", "йоу",
           "понял", "ясно", "логично", "интересно", "здорово", "нравится"},
    "en": {"good", "great", "awesome", "excellent", "perfect", "thanks", "please",
           "happy", "glad", "wonderful", "amazing", "brilliant", "correct", "yes",
           "sure", "right", "done", "works", "success", "nice", "cool", "love",
           "understood", "clear", "interesting", "fantastic", "superb"}
}

NEGATIVE_WORDS = {
    "ru": {"плохо", "ужасно", "кошмар", "говно", "дерьмо", "бред", "чушь",
           "ошибка", "сломал", "не работает", "фигня", "херня", "дичь",
           "злюсь", "бесит", "раздражает", "ненавижу", "устал", "задолбал",
           "разочарован", "обидно", "жалко", "страшно", "больно", "кризис",
           "провал", "катастрофа", "хуже", "ненормально", "идиот", "дурак",
           "тупо", "глупо", "бессмысленно", "зря", "напрасно"},
    "en": {"bad", "terrible", "horrible", "shit", "damn", "crap", "nonsense",
           "error", "broken", "doesn't work", "stupid", "ridiculous", "awful",
           "angry", "furious", "annoying", "hate", "tired", "frustrated",
           "disappointed", "worst", "disaster", "failure", "useless", "dumb",
           "pointless", "waste", "sucks"}
}

HEDGE_WORDS = {"maybe", "perhaps", "might", "possibly", "i think", "perhaps",
               "может", "возможно", "наверное", "кажется", "пожалуй", "вроде"}

URGENCY_WORDS = {"срочно", "быстро", "сейчас", "немедленно", "urgent", "asap",
                 "now", "immediately", "быстрее", "тороплюсь", "спешу"}


# ============ ANALYSIS ============

def analyze_text(text):
    """Analyze a single text for flёр metrics."""
    text_lower = text.lower()
    words = re.findall(r'[a-zA-Zа-яА-ЯёЁ0-9_]+', text_lower)
    word_count = len(words) or 1
    
    # Count positive/negative
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS["ru"] or w in POSITIVE_WORDS["en"])
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS["ru"] or w in NEGATIVE_WORDS["en"])
    
    # Tone: -1.0 to +1.0
    total_sentiment = pos_count + neg_count
    if total_sentiment > 0:
        tone = (pos_count - neg_count) / total_sentiment
    else:
        tone = 0.0
    
    # Energy: based on caps, exclamation, emoji, word density
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    excl_count = text.count('!') + text.count('！')
    emoji_count = len(re.findall('[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF\U00002702-\U000027B0\U0001FA00-\U0001FA6F]', text))
    question_count = text.count('?') + text.count('？')
    
    energy = min(10, int(
        caps_ratio * 20 +
        excl_count * 1.5 +
        emoji_count * 2 +
        question_count * 0.5 +
        (word_count / 20)
    ))
    
    # Tension: neg words + caps + urgency
    urgency_count = sum(1 for w in words if w in URGENCY_WORDS)
    tension = min(10, int(
        neg_count * 2 +
        caps_ratio * 15 +
        urgency_count * 3
    ))
    
    # Engagement: word count + questions + length
    engagement = min(10, int(
        word_count / 10 +
        question_count * 1.5 +
        len(text) / 200
    ))
    
    # Contamination: heavy negative + aggressive
    aggressive = sum(1 for w in words if w in {"идиот", "дурак", "stupid", "dumb", "shit", "говно", "дерьмо"})
    contamination = min(10, int(
        neg_count * 3 +
        aggressive * 5 +
        caps_ratio * 10
    ))
    
    return {
        "tone": round(tone, 2),
        "energy": energy,
        "tension": tension,
        "engagement": engagement,
        "contamination": contamination,
        "positive_words": pos_count,
        "negative_words": neg_count,
        "word_count": word_count,
    }


def analyze_session(messages):
    """Analyze a full session (list of message strings) for flёр."""
    if not messages:
        return None
    
    # Per-message analysis
    analyses = [analyze_text(msg) for msg in messages]
    
    # Aggregate flёр
    avg_tone = sum(a["tone"] for a in analyses) / len(analyses)
    avg_energy = sum(a["energy"] for a in analyses) / len(analyses)
    avg_tension = sum(a["tension"] for a in analyses) / len(analyses)
    avg_engagement = sum(a["engagement"] for a in analyses) / len(analyses)
    max_contamination = max(a["contamination"] for a in analyses)
    
    # Aftertaste: based on last 3 messages
    last_3 = analyses[-3:]
    aftertaste_tone = sum(a["tone"] for a in last_3) / len(last_3)
    if aftertaste_tone > 0.2:
        aftertaste = "positive"
    elif aftertaste_tone < -0.2:
        aftertaste = "negative"
    else:
        aftertaste = "neutral"
    
    # Contamination detection: sudden negative shifts
    contamination_events = []
    for i in range(1, len(analyses)):
        tone_shift = analyses[i]["tone"] - analyses[i-1]["tone"]
        if tone_shift < -0.5:
            contamination_events.append({
                "message_index": i,
                "tone_shift": round(tone_shift, 2),
                "contamination": analyses[i]["contamination"]
            })
    
    return {
        "message_count": len(messages),
        "fler": {
            "tone": round(avg_tone, 2),
            "energy": round(avg_energy, 1),
            "tension": round(avg_tension, 1),
            "engagement": round(avg_engagement, 1),
            "contamination": max_contamination,
        },
        "aftertaste": aftertaste,
        "contamination_events": contamination_events,
        "per_message": analyses,
    }


# ============ DATABASE ============

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS fler_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER,
            tone REAL,
            energy REAL,
            tension REAL,
            engagement REAL,
            contamination INTEGER,
            aftertaste TEXT,
            contamination_events TEXT,
            raw_data TEXT
        )
    """)
    conn.commit()
    return conn


def save_session(session_id, result):
    """Save analysis result to database."""
    conn = init_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO fler_sessions 
        (session_id, message_count, tone, energy, tension, engagement, 
         contamination, aftertaste, contamination_events, raw_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        result["message_count"],
        result["fler"]["tone"],
        result["fler"]["energy"],
        result["fler"]["tension"],
        result["fler"]["engagement"],
        result["fler"]["contamination"],
        result["aftertaste"],
        json.dumps(result["contamination_events"]),
        json.dumps(result, ensure_ascii=False)
    ))
    conn.commit()
    conn.close()


def get_stats():
    """Get overall flёр statistics."""
    conn = init_db()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM fler_sessions")
    total = c.fetchone()[0]
    
    c.execute("SELECT AVG(tone), AVG(energy), AVG(tension), AVG(engagement), AVG(contamination) FROM fler_sessions")
    avgs = c.fetchone()
    
    c.execute("SELECT aftertaste, COUNT(*) FROM fler_sessions GROUP BY aftertaste")
    aftertastes = dict(c.fetchall())
    
    c.execute("SELECT * FROM fler_sessions ORDER BY ts DESC LIMIT 5")
    recent = c.fetchall()
    
    conn.close()
    
    return {
        "total_sessions": total,
        "averages": {
            "tone": round(avgs[0] or 0, 2),
            "energy": round(avgs[1] or 0, 1),
            "tension": round(avgs[2] or 0, 1),
            "engagement": round(avgs[3] or 0, 1),
            "contamination": round(avgs[4] or 0, 1),
        },
        "aftertastes": aftertastes,
        "recent_sessions": recent,
    }


# ============ DEMO ============

DEMO_SESSIONS = {
    "positive": [
        "Привет! Как дела?",
        "Отлично, спасибо! Работаю над новым проектом.",
        "Супер, это здорово! Расскажи подробнее.",
        "Да, получилось! Молодец, всё работает идеально!",
    ],
    "negative": [
        "Опять ошибка! Это не работает!",
        "КАКОЙ КОШМАР! Всё сломалось, я устал это чинить!",
        "Бред какой-то. Тупо не работает. Говно, а не система.",
        "Всё, хватит. Разочарован. Ничего не получается.",
    ],
    "mixed": [
        "Привет, помоги настроить сервер.",
        "Ошибка при подключении. Что делать?",
        "Ладно, попробовал — не помогло. Бесит.",
        "Ок, разобрался. Спасибо, работает!",
    ],
    "contaminated": [
        "Начинаем проект, давай!",
        "Отличный план, согласен!",
        "Подожди... а это кто написал? Бред какой-то.",
        "Всё, отмена. Это говно, переделывай всё!",
    ],
}


def demo():
    """Run demo analysis on sample sessions."""
    sep = "-" * 50
    print("=" * 60)
    print("  FLER ENGINE - DEMO")
    print("=" * 60)
    
    for name, messages in DEMO_SESSIONS.items():
        result = analyze_session(messages)
        fler = result["fler"]
        
        print()
        print(sep)
        print("  Session: " + name.upper())
        print(sep)
        
        for i, msg in enumerate(messages):
            a = result["per_message"][i]
            if a["tone"] > 0.2:
                tone_icon = "[+]"
            elif a["tone"] < -0.2:
                tone_icon = "[-]"
            else:
                tone_icon = "[.]"
            print("  " + tone_icon + " " + msg[:50])
            line = "     tone={:+.2f} energy={} tension={}".format(
                a["tone"], a["energy"], a["tension"])
            print(line)
        
        print()
        print("  FLER:")
        tone_str = "{:+.2f}".format(fler["tone"])
        print("    Tone:        " + tone_str)
        print("    Energy:      " + str(fler["energy"]) + "/10")
        print("    Tension:     " + str(fler["tension"]) + "/10")
        print("    Engagement:  " + str(fler["engagement"]) + "/10")
        print("    Contaminate: " + str(fler["contamination"]) + "/10")
        print("  AFTERtaste: " + result["aftertaste"])
        
        if result["contamination_events"]:
            print("  CONTAMINATION:")
            for evt in result["contamination_events"]:
                print("    ! Message #{}: tone shift {}".format(
                    evt["message_index"], evt["tone_shift"]))
        
        save_session(name, result)
    
    print()
    print("=" * 60)
    print("  STATS")
    print("=" * 60)
    stats = get_stats()
    print("  Sessions: " + str(stats["total_sessions"]))
    print("  Avg tone: " + "{:+.2f}".format(stats["averages"]["tone"]))
    print("  Avg energy: " + str(stats["averages"]["energy"]))
    print("  Aftertastes: " + str(stats["aftertastes"]))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "demo":
        demo()
    elif cmd == "analyze":
        if len(sys.argv) < 3:
            print("Usage: fler_engine.py analyze <file>")
            sys.exit(1)
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            messages = [line.strip() for line in f if line.strip()]
        result = analyze_session(messages)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif cmd == "stats":
        stats = get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
