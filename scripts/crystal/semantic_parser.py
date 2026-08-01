"""
Crystal v3 — Семантический парсер
Извлекает СМЫСЛ из сообщений, а не ключевые слова.


# Revisit: when semantic parsing logic, LLM provider, or intent extraction changes. Last touched: 2026-07-02.
Использует LLM (OpenCode Zen) для batch-анализа:
- Берёт батч сообщений
- Модель анализирует: намерения, фрустрацию, цели, контекст
- Возвращает структурированный результат с РЕАЛЬНЫМ пониманием
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from .config import STATE_DB, CACHE_DIR
from .models import save_json

# Импортируем unified LLM клиент с фоллбэком
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
try:
    from llm_client import call_llm
except ImportError:
    from openrouter_client import call_llm


class SemanticParser:
    """
    Семантический парсер — извлекает СМЫСЛ из сообщений.
    
    Не regex, не ключевые слова. Модель ЧИТАЕТ и ПОНИМАЕТ:
    - Что человек ХОЧЕТ сделать
    - Что его БЕСИТ и почему
    - К ЧЕМУ он стремится
    - Что мешает
    """
    
    BATCH_SIZE = 25  # Сообщений в одном запросе к модели
    
    # Промпт для анализа — самое важное
    ANALYSIS_PROMPT = """Проанализируй сообщения пользователя из чата с AI-ассистентом.

Извлеки из сообщений:

1. ЧЕГО ЧЕЛОВЕК ХОЧЕТ (goals) — конкретные цели, не абстракции
2. ЧТО БЕСИТ (frustration) — что не работает, что мешает, что вызывает злость
3. ЧЕМ ЗАНЯТ (activities) — что делает, над чем работает
4. КОНТЕКСТ (context) — что уже пробовал, что получилось, что нет
5. ОТНОШЕНИЕ К АССИСТЕНТУ (relationship) — доверяет ли, разочарован ли, ждёт ли чего-то

ВАЖНЫЕ ПРАВИЛА:
- Не повторяй слова пользователя дословно — извлекай СМЫСЛ
- Если человек злится — это маркер что процесс сломан, не его характер
- Если человек говорит "заглушки бесполезны" — он имеет в виду что пустышки искажают информацию
- Если человек упоминает фильм "Она" — он хочет чтобы ассистент стал партнёром, не инструментом
- Если человек говорит "заработок" — он не ХОЧЕТ зарабатывать, а ВЫНУЖДЕН (чтобы есть)
- Если человек говорит "хватит болтать" — он хочет ДЕЙСТВИЙ, не аналитики

Формат ответа — строго JSON:
{
  "goals": [{"goal": "...", "why": "...", "urgency": "high/medium/low"}],
  "frustration": [{"what": "...", "why": "...", "marker": "true — это индикатор сломанного процесса"}],
  "activities": [{"activity": "...", "status": "doing/tried/abandoned"}],
  "context": [{"key": "...", "value": "..."}],
  "relationship": {"trust_level": "high/medium/low", "expectations": "...", "pain_points": ["..."]}
}

Сообщения:
"""

    def __init__(self):
        self.db_path = STATE_DB
        self.cache_file = os.path.join(CACHE_DIR, "semantic_analysis.json")
    
    def parse(self, days: int = 30, force: bool = False) -> dict:
        """
        Семантический анализ переписки.
        Возвращает реальное понимание того ЧТО человек хочет и ЧТО его бесит.
        """
        # Проверяем кэш
        if not force and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                if cached.get("parsed_at"):
                    cached_date = datetime.fromisoformat(cached["parsed_at"])
                    if (datetime.now() - cached_date).total_seconds() < 3600:  # 1 час
                        print("  Using cached semantic analysis")
                        return cached
            except Exception:
                pass
        
        print(f"[Semantic] Анализ за {days} дней...")
        
        # 1. Читаем сообщения
        messages = self._read_user_messages(days)
        print(f"  Сообщений для анализа: {len(messages)}")
        
        if not messages:
            return {"goals": [], "frustration": [], "activities": [], "context": [], "relationship": {}}
        
        # 2. Разбиваем на батчи и анализируем
        all_results = []
        total_batches = (len(messages) - 1) // self.BATCH_SIZE + 1
        
        for i in range(0, len(messages), self.BATCH_SIZE):
            batch = messages[i:i + self.BATCH_SIZE]
            batch_text = self._format_batch(batch)
            
            print(f"  Батч {i // self.BATCH_SIZE + 1}/{total_batches}...")
            result = self._analyze_batch(batch_text)
            
            if result:
                all_results.append(result)
        
        print(f"  Успешных батчей: {len(all_results)}/{total_batches}")
        
        # 3. Агрегируем результаты
        aggregated = self._aggregate(all_results)
        
        # 4. Кэшируем
        aggregated["parsed_at"] = datetime.now().isoformat()
        aggregated["total_messages"] = len(messages)
        save_json(aggregated, self.cache_file)
        
        return aggregated
    
    def _read_user_messages(self, days: int) -> list:
        """Читаем ТОЛЬКО сообщения пользователя с умным сэмплингом"""
        if not os.path.exists(self.db_path):
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_ts = cutoff.timestamp()
        
        messages = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT content, timestamp
                FROM messages
                WHERE role = 'user'
                AND timestamp > ?
                AND content IS NOT NULL
                AND LENGTH(content) > 10
                ORDER BY timestamp
            """, (cutoff_ts,))
            
            all_msgs = []
            for row in cursor.fetchall():
                content = row[0]
                if self._is_real_user_message(content):
                    all_msgs.append({
                        "text": content[:500],  # Ограничиваем длину для экономии токенов
                        "time": datetime.fromtimestamp(row[1]).isoformat(),
                    })
            
            conn.close()
            
            # УМНЫЙ СЭМПЛИНГ: не все 3500+, а представительные
            # Берём: последние 50 + равномерную выборку из оставшихся
            if len(all_msgs) > 100:
                # Последние 50 — самое актуальное
                recent = all_msgs[-50:]
                # Равномерная выборка из остальных
                rest = all_msgs[:-50]
                step = max(1, len(rest) // 50)
                sampled = rest[::step][:50]
                messages = sampled + recent
                print(f"  Сэмплинг: {len(all_msgs)} -> {len(messages)} (равномерный + последние 50)")
            else:
                messages = all_msgs
            
        except Exception as e:
            print(f"  Ошибка чтения: {e}")
        
        return messages
    
    def _is_real_user_message(self, content: str) -> bool:
        """Проверяем что это РЕАЛЬНОЕ сообщение пользователя"""
        skip_patterns = [
            "[Assistant Rules]",
            "[LOAD_SKILL:",
            "## Available Skills",
            "[CONTEXT COMPACTION",
            "## Historical",
            "--- END OF CONTEXT",
        ]
        for p in skip_patterns:
            if p in content:
                return False
        return len(content.strip()) >= 5
    
    def _format_batch(self, batch: list) -> str:
        """Форматируем батч для отправки модели"""
        lines = []
        for i, msg in enumerate(batch, 1):
            lines.append(f"[{i}] ({msg['time'][:16]}): {msg['text']}")
        return "\n".join(lines)
    
    def _analyze_batch(self, batch_text: str) -> Optional[dict]:
        """Отправляем батч модели для анализа через OpenCode Zen"""
        prompt = self.ANALYSIS_PROMPT + batch_text
        
        try:
            response = call_llm(prompt, model="mimo-v2.5-free", max_tokens=2000, temperature=0.3)
            
            if not response:
                print("  Модель не вернула ответ")
                return None
            
            # Парсим JSON из ответа модели
            # Модель может вернуть JSON в markdown блоке или напрямую
            json_str = response
            
            # Убираем markdown блок если есть
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            # Ищем JSON объект
            start = json_str.find("{")
            end = json_str.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = json_str[start:end]
            
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            print(f"  Модель вернула не JSON: {response[:200] if response else 'empty'}")
            return None
        except Exception as e:
            print(f"  Ошибка анализа: {e}")
            return None
    
    def _aggregate(self, results: list) -> dict:
        """Агрегируем результаты всех батчей"""
        if not results:
            return {"goals": [], "frustration": [], "activities": [], "context": [], "relationship": {}}
        
        all_goals = []
        all_frustration = []
        all_activities = []
        all_context = []
        trust_levels = []
        all_pain_points = []
        
        for r in results:
            all_goals.extend(r.get("goals", []))
            all_frustration.extend(r.get("frustration", []))
            all_activities.extend(r.get("activities", []))
            all_context.extend(r.get("context", []))
            rel = r.get("relationship", {})
            if rel.get("trust_level"):
                trust_levels.append(rel["trust_level"])
            all_pain_points.extend(rel.get("pain_points", []))
        
        # Дедупликация по тексту
        def dedup(items, key_field):
            seen = set()
            unique = []
            for item in items:
                k = item.get(key_field, "")[:50].lower()
                if k and k not in seen:
                    seen.add(k)
                    unique.append(item)
            return unique
        
        unique_goals = dedup(all_goals, "goal")
        unique_frust = dedup(all_frustration, "what")
        
        # Самый частый trust level
        from collections import Counter
        trust = Counter(trust_levels).most_common(1)[0][0] if trust_levels else "medium"
        
        return {
            "goals": unique_goals[:10],
            "frustration": unique_frust[:10],
            "activities": all_activities[:15],
            "context": all_context[:10],
            "relationship": {
                "trust_level": trust,
                "pain_points": list(set(all_pain_points))[:5],
            },
        }
