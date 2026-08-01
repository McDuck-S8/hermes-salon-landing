"""
Crystal v3 — Модуль анализа переписки
Анализирует ВСЮ историю сообщений для извлечения инсайтов
+ Анализ намерений, трекинг целей, предсказание потребностей

# Revisit: when conversation analysis depth, caching strategy, or insight extraction changes. Last touched: 2026-07-02.
"""

import sqlite3
import os
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from .config import STATE_DB, CACHE_DIR
from .models import save_json


class ConversationAnalyzer:
    """Анализатор полной переписки"""
    
    # Ключевые слова для поиска инсайтов
    INSIGHT_KEYWORDS = [
        "идея", "план", "стратегия", "подход", "метод", "способ",
        "проблема", "решение", "улучшение", "оптимизация", "автоматизация",
        "важно", "критично", "приоритет", "срочно", "нужно",
        "паттерн", "тенденция", "тренд", "закономерность",
        "инсайт", "наблюдение", "вывод", "открытие", "понимание",
    ]
    
    # Паттерны для поиска идей
    IDEA_PATTERNS = [
        r"можно\s+(сделать|создать|добавить|улучшить|оптимизировать)",
        r"стоит\s+(попробовать|сделать|добавить)",
        r"хочу\s+(чтобы|сделать|получить|видеть)",
        r"надо\s+(бы|было бы|сделать|добавить)",
        r"если\s+(бы|мы|сделать)",
        r"было бы\s+(хорошо|классно|идеально)",
        r"а\s+(что\s+если|можно|если)",
    ]
    
    def __init__(self):
        self.db_path = STATE_DB
        self.cache_file = os.path.join(CACHE_DIR, "conversation_analysis.json")
    
    def analyze_full(self, days: int = 30) -> dict:
        """Полный анализ переписки за N дней"""
        print(f"[Analyzer] Анализ переписки за {days} дней...")
        
        # 1. Читаем все сообщения
        messages = self._read_messages(days)
        print(f"  Загружено сообщений: {len(messages)}")
        
        # 2. Анализируем по категориям
        insights = self._extract_insights(messages)
        ideas = self._extract_ideas(messages)
        problems = self._extract_problems(messages)
        workflows = self._extract_workflows(messages)
        patterns = self._extract_patterns(messages)
        
        # 3. НОВОЕ: Анализ намерений и целей
        intents = self._analyze_intents(messages)
        goals = self._track_goals(messages)
        predictions = self._predict_needs(messages, intents)
        frustration = self._detect_frustration(messages)
        
        print(f"  Намерений: {len(intents)}, Целей: {len(goals)}, Предсказаний: {len(predictions)}")
        print(f"  Фрустраций: {frustration['total']}")
        
        # 4. Формируем результат
        result = {
            "analyzed_at": datetime.now().isoformat(),
            "period_days": days,
            "total_messages": len(messages),
            "insights": insights,
            "ideas": ideas,
            "problems": problems,
            "workflows": workflows,
            "patterns": patterns,
            # НОВОЕ: Намерения, цели, предсказания
            "intents": intents,
            "goals": goals,
            "predicted_needs": predictions,
            "frustration": frustration,
            "summary": self._generate_summary(insights, ideas, problems, workflows, intents, goals),
        }
        
        # 5. Кэшируем
        save_json(result, self.cache_file)
        
        return result
    
    def _read_messages(self, days: int) -> list:
        """Читать сообщения за период"""
        if not os.path.exists(self.db_path):
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_ts = cutoff.timestamp()
        
        messages = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, session_id, role, content, timestamp
                FROM messages
                WHERE role IN ('user', 'assistant')
                AND timestamp > ?
                AND content IS NOT NULL
                AND LENGTH(content) > 20
                ORDER BY timestamp
            """, (cutoff_ts,))
            
            for row in cursor.fetchall():
                content = row["content"]
                
                # Фильтруем мусор
                if self._is_noise(content):
                    continue
                
                messages.append({
                    "id": row["id"],
                    "session_id": row["session_id"],
                    "role": row["role"],
                    "content": content,
                    "timestamp": datetime.fromtimestamp(row["timestamp"]),
                })
            
            conn.close()
        except Exception as e:
            print(f"  Ошибка чтения: {e}")
        
        return messages
    
    def _is_noise(self, content: str) -> bool:
        """Проверить, является ли сообщение мусором"""
        noise_patterns = [
            "[CONTEXT COMPACTION",
            "Earlier turns were compacted",
            "treat it as background reference",
            "NOT as active instructions",
            "Treat ONLY the latest user message",
            "## Historical Task Snapshot",
            "## Historical In-Progress State",
            "## Historical Remaining Work",
            "## Critical Context",
            "--- END OF CONTEXT SUMMARY",
        ]
        
        content_lower = content.lower()
        for pattern in noise_patterns:
            if pattern.lower() in content_lower:
                return True
        
        if len(content) < 30 or len(content) > 2000:
            return True
        
        return False
    
    def _extract_insights(self, messages: list) -> list:
        """Извлечь инсайты из сообщений"""
        insights = []
        
        for msg in messages:
            if msg["role"] != "user":
                continue
            
            content = msg["content"].lower()
            
            for keyword in self.INSIGHT_KEYWORDS:
                if keyword in content:
                    sentences = re.split(r'[.!?]+', msg["content"])
                    for sent in sentences:
                        if keyword in sent.lower() and len(sent.strip()) > 20:
                            insights.append({
                                "text": sent.strip()[:300],
                                "keyword": keyword,
                                "session_id": msg["session_id"],
                                "timestamp": msg["timestamp"].isoformat(),
                            })
                            break
                    break
        
        unique = []
        seen = set()
        for insight in insights:
            key = insight["text"][:100]
            if key not in seen:
                seen.add(key)
                unique.append(insight)
        
        return unique[:50]
    
    def _extract_ideas(self, messages: list) -> list:
        """Извлечь идеи и предложения"""
        ideas = []
        
        strong_patterns = [
            (r"стоит\s+(сделать|добавить|создать|внедрить|попробовать)", "action"),
            (r"хочу\s+(чтобы|видеть|получить|сделать)", "desire"),
            (r"надо\s+(сделать|добавить|создать|использовать)", "need"),
            (r"можно\s+(автоматизировать|оптимизировать|улучшить)", "improvement"),
            (r"а\s+что\s+если\s+(сделать|создать|добавить)", "experiment"),
        ]
        
        for msg in messages:
            if msg["role"] != "user":
                continue
            
            content = msg["content"]
            
            for pattern, category in strong_patterns:
                matches = list(re.finditer(pattern, content.lower()))
                if matches:
                    for match in matches[:1]:
                        start = max(0, content.rfind('.', 0, match.start()) + 1)
                        end = content.find('.', match.end())
                        if end == -1:
                            end = min(len(content), match.end() + 200)
                        
                        idea_text = content[start:end].strip()
                        
                        if len(idea_text) > 40 and not idea_text.startswith('('):
                            ideas.append({
                                "text": idea_text[:300],
                                "category": category,
                                "session_id": msg["session_id"],
                                "timestamp": msg["timestamp"].isoformat(),
                            })
                    break
        
        unique = []
        seen = set()
        for idea in ideas:
            key = idea["text"][:80].lower().strip()
            if key not in seen and len(key) > 30:
                seen.add(key)
                unique.append(idea)
        
        return unique[:30]
    
    def _extract_problems(self, messages: list) -> list:
        """Извлечь проблемы и жалобы"""
        problems = []
        
        problem_keywords = [
            "проблема", "ошибка", "баг", "глюк", "не работает",
            "сломал", "упал", "вылетел", "timeout", "failed",
            "хочу чтобы", "надо бы", "нужно бы", "неудобно",
        ]
        
        for msg in messages:
            if msg["role"] != "user":
                continue
            
            content = msg["content"].lower()
            
            for kw in problem_keywords:
                if kw in content:
                    sentences = re.split(r'[.!?]+', msg["content"])
                    for sent in sentences:
                        if kw in sent.lower() and len(sent.strip()) > 20:
                            problems.append({
                                "text": sent.strip()[:300],
                                "keyword": kw,
                                "session_id": msg["session_id"],
                                "timestamp": msg["timestamp"].isoformat(),
                            })
                            break
                    break
        
        unique = []
        seen = set()
        for prob in problems:
            key = prob["text"][:100]
            if key not in seen:
                seen.add(key)
                unique.append(prob)
        
        return unique[:50]
    
    def _extract_workflows(self, messages: list) -> list:
        """Извлечь описанные рабочие процессы"""
        workflows = []
        
        workflow_keywords = [
            "процесс", "workflow", "pipeline", "этап", "шаг",
            "алгоритм", "схема", "порядок", "последовательность",
        ]
        
        for msg in messages:
            if msg["role"] != "user":
                continue
            
            content = msg["content"].lower()
            
            for kw in workflow_keywords:
                if kw in content:
                    paragraphs = msg["content"].split('\n\n')
                    for para in paragraphs:
                        if kw in para.lower() and len(para.strip()) > 50:
                            workflows.append({
                                "text": para.strip()[:500],
                                "keyword": kw,
                                "session_id": msg["session_id"],
                                "timestamp": msg["timestamp"].isoformat(),
                            })
                            break
                    break
        
        unique = []
        seen = set()
        for wf in workflows:
            key = wf["text"][:100]
            if key not in seen:
                seen.add(key)
                unique.append(wf)
        
        return unique[:30]
    
    def _extract_patterns(self, messages: list) -> dict:
        """Извлечь паттерны поведения"""
        daily = Counter()
        for msg in messages:
            if msg["role"] == "user":
                day = msg["timestamp"].strftime("%Y-%m-%d")
                daily[day] += 1
        
        topic_counter = Counter()
        for msg in messages:
            if msg["role"] == "user":
                words = msg["content"].lower().split()
                for word in words:
                    if len(word) > 4:
                        topic_counter[word] += 1
        
        return {
            "daily_activity": dict(daily.most_common(30)),
            "top_topics": dict(topic_counter.most_common(20)),
        }
    
    # ══════════════════════════════════════════════════════════════
    # НОВОЕ: Анализ намерений, трекинг целей, предсказание потребностей
    # ══════════════════════════════════════════════════════════════
    
    def _analyze_intents(self, messages: list) -> list:
        """Анализ НАМЕРЕНИЙ — что пользователь ПЫТАЕТСЯ сделать"""
        intents = []
        
        # Паттерны намерений (что пользователь хочет достичь)
        intent_patterns = [
            # Заработок / бизнес
            (r"(заработ|деньги|доход|бизнес|монетиз|продав|клиент|услуг)", "earn_money", "Заработок/бизнес"),
            # Исследование
            (r"(исслед|найти|узнать|изучить|проанализир|сравни)", "research", "Исследование"),
            # Создание
            (r"(создать|сделать|написать|собрать|построить|разработать)", "build", "Создание/разработка"),
            # Настройка
            (r"(настроить|запустить|подключить|установить|внедрить)", "setup", "Настройка/внедрение"),
            # Исправление
            (r"(чинит|исправ|ошибк|баг|проблем|не работ|сломал)", "fix", "Исправление"),
            # Оптимизация
            (r"(оптимиз|улучш|ускор|автоматиз|эффективн)", "optimize", "Оптимизация"),
            # Понимание
            (r"(понять|разобр|объясни|как работает|что делает)", "understand", "Понимание"),
            # Планирование
            (r"(план|стратег|этап|шаг|дорожн|roadmap)", "plan", "Планирование"),
        ]
        
        # Группируем сообщения по сессиям
        sessions = defaultdict(list)
        for msg in messages:
            if msg["role"] == "user":
                sessions[msg["session_id"]].append(msg)
        
        # Анализируем каждую сессию
        for session_id, session_msgs in sessions.items():
            session_intents = set()
            for msg in session_msgs:
                content = msg["content"].lower()
                for pattern, intent_type, intent_name in intent_patterns:
                    if re.search(pattern, content):
                        session_intents.add((intent_type, intent_name))
            
            # Записываем намерения сессии
            for intent_type, intent_name in session_intents:
                intents.append({
                    "intent": intent_type,
                    "name": intent_name,
                    "session_id": session_id,
                    "message_count": len(session_msgs),
                    "timestamp": session_msgs[0]["timestamp"].isoformat(),
                })
        
        # Дедупликация и приоритизация
        intent_counts = Counter(i["intent"] for i in intents)
        unique_intents = []
        seen = set()
        for intent in intents:
            key = intent["intent"]
            if key not in seen:
                seen.add(key)
                intent["frequency"] = intent_counts[key]
                unique_intents.append(intent)
        
        return sorted(unique_intents, key=lambda x: x["frequency"], reverse=True)
    
    def _track_goals(self, messages: list) -> list:
        """Трекинг ЦЕЛЕЙ — что пользователь хочет достичь"""
        goals = []
        
        # Паттерны целей (конкретные желаемые результаты)
        goal_patterns = [
            (r"(хочу|желаю|нужно|надо)\s+(чтобы|получить|сделать|видеть|иметь)", "desired_outcome"),
            (r"(цель|задач|результат|эффект)\s*[:=]?\s*", "explicit_goal"),
            (r"(должен|должна|должно)\s+(быть|стать|сделать)", "expected_state"),
            (r"(план|стратегия|roadmap)\s*[:=]?\s*", "planned_path"),
        ]
        
        for msg in messages:
            if msg["role"] != "user":
                continue
            
            content = msg["content"]
            content_lower = content.lower()
            
            for pattern, goal_type in goal_patterns:
                matches = list(re.finditer(pattern, content_lower))
                for match in matches[:2]:  # Макс 2 на сообщение
                    start = max(0, content.rfind('.', 0, match.start()) + 1)
                    end = content.find('.', match.end())
                    if end == -1:
                        end = min(len(content), match.end() + 200)
                    
                    goal_text = content[start:end].strip()
                    if len(goal_text) > 30:
                        goals.append({
                            "text": goal_text[:300],
                            "type": goal_type,
                            "session_id": msg["session_id"],
                            "timestamp": msg["timestamp"].isoformat(),
                        })
        
        # Дедупликация
        unique = []
        seen = set()
        for goal in goals:
            key = goal["text"][:80].lower()
            if key not in seen and len(key) > 20:
                seen.add(key)
                unique.append(goal)
        
        return unique[:30]
    
    def _predict_needs(self, messages: list, intents: list) -> list:
        """Предсказание ПОТРЕБНОСТЕЙ — что понадобится дальше"""
        predictions = []
        
        # На основе текущих намерений предсказываем следующие шаги
        intent_predictions = {
            "earn_money": [
                "Бизнес-план для метода заработка",
                "Анализ конкурентов",
                "Оценка стартовых затрат",
                "Настройка автоматизации",
                "Метрики и KPI",
            ],
            "research": [
                "Сравнительный анализ",
                "Рекомендации на основе данных",
                "Дорожная карта внедрения",
            ],
            "build": [
                "Техническое задание",
                "Архитектура решения",
                "Тестирование и отладка",
                "Деплой и мониторинг",
            ],
            "setup": [
                "Инструкция по настройке",
                "Проверка зависимостей",
                "Тестирование работоспособности",
            ],
            "fix": [
                "Диагностика проблемы",
                "Поиск корневой причины",
                "Исправление и тестирование",
            ],
            "optimize": [
                "Бенчмаркинг текущего состояния",
                "Идентификация узких мест",
                "Внедрение улучшений",
            ],
            "understand": [
                "Документация и объяснения",
                "Примеры использования",
                "Архитектурный обзор",
            ],
            "plan": [
                "Разбивка на этапы",
                "Оценка ресурсов",
                "Определение приоритетов",
            ],
        }
        
        # Считаем частоту намерений из уже подсчитанной частоты
        intent_counts = Counter(i["intent"] for i in intents)
        
        # Генерируем предсказания на основе самых частых намерений
        for intent, count in intent_counts.most_common(5):
            if intent in intent_predictions:
                # Берём frequency из intents (это реальная частота, не уникальные сессии)
                freq = next((i["frequency"] for i in intents if i["intent"] == intent), count)
                confidence = min(freq / 50, 1.0)
                for need in intent_predictions[intent]:
                    predictions.append({
                        "need": need,
                        "based_on": intent,
                        "confidence": confidence,
                        "reason": f"Пользователь часто занимается: {intent} ({freq} раз)",
                    })
        
        return predictions[:20]
    
    def _detect_frustration(self, messages: list) -> dict:
        """Детекция ФРУСТРАЦИИ — когда и почему пользователь злится"""
        frustrations = []
        
        # Паттерны фрустрации
        frustration_patterns = [
            (r"(хватит|прекрати|остановис|хватит болтать)", "stop_talking", "Хватит болтать"),
            (r"(зл|бесит|раздраж|надоел|достал)", "anger", "Злость/раздражение"),
            (r"(не работает|сломал|упал|вылетел|ошибк)", "system_failure", "Системная ошибка"),
            (r"(долго|жду|медленн|тормозит|завис)", "slow", "Медленная работа"),
            (r"(непонятно|не понимаю|запутал|путаешь)", "confusion", "Непонимание"),
            (r"(мусор|шаблон|заглушк|пустышк)", "low_quality", "Низкое качество"),
            (r"(просто сделай|делай|не спрашивай|хватит спрашивать)", "action_not_talk", "Требование действий"),
        ]
        
        for msg in messages:
            if msg["role"] != "user":
                continue
            
            content = msg["content"]
            content_lower = content.lower()
            
            for pattern, frustr_type, frustr_name in frustration_patterns:
                if re.search(pattern, content_lower):
                    frustrations.append({
                        "type": frustr_type,
                        "name": frustr_name,
                        "text": content[:200],
                        "session_id": msg["session_id"],
                        "timestamp": msg["timestamp"].isoformat(),
                    })
                    break  # Одно сообщение = одна фрустрация
        
        # Группируем по типам
        type_counts = Counter(f["type"] for f in frustrations)
        
        return {
            "events": frustrations[:20],
            "by_type": dict(type_counts.most_common()),
            "total": len(frustrations),
        }
    
    def _generate_summary(self, insights: list, ideas: list, problems: list, 
                          workflows: list, intents: list = None, goals: list = None) -> str:
        """Сгенерировать краткую сводку"""
        parts = []
        
        if insights:
            parts.append(f"Найдено {len(insights)} инсайтов")
        if ideas:
            parts.append(f"{len(ideas)} идей и предложений")
        if problems:
            parts.append(f"{len(problems)} проблем")
        if workflows:
            parts.append(f"{len(workflows)} описаний процессов")
        if intents:
            top_intent = intents[0]["name"] if intents else "нет"
            parts.append(f"Основное намерение: {top_intent} ({len(intents)} типов)")
        if goals:
            parts.append(f"{len(goals)} целей выражено")
        
        return ", ".join(parts) if parts else "Анализ завершён"
    
    def get_cached(self) -> dict:
        """Получить кэшированный анализ"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
