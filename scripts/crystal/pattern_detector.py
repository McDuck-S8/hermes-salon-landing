"""
Crystal v3 — Модуль 2: Pattern Detector
Находит повторяющиеся паттерны из сигналов
"""

# Revisit: when pattern types, detection algorithms, or signal-to-pattern mapping changes. Last touched: 2026-07-02.


from collections import Counter, defaultdict
from .models import Signal, Pattern


class PatternDetector:
    """Находит повторяющиеся паттерны из сигналов"""

    # Пороги для паттернов
    PATTERN_TYPES = {
        "correction_loop": {
            "description": "Пользовательчасто поправляет одно и то же",
            "min_frequency": 2,
            "severity_boost": 0.2,
        },
        "frustration_spike": {
            "description": "Много фрустрации за короткий период",
            "min_frequency": 3,
            "severity_boost": 0.3,
        },
        "missing_knowledge": {
            "description": "Пользователь постоянно спрашивает одно и то же",
            "min_frequency": 2,
            "severity_boost": 0.15,
        },
        "workflow_success": {
            "description": "Успешный паттерн, который стоит повторять",
            "min_frequency": 2,
            "severity_boost": -0.1,  # позитивный
        },
        "unmet_need": {
            "description": "Потребность, которая не закрывается",
            "min_frequency": 2,
            "severity_boost": 0.1,
        },
        "department_focus": {
            "description": "Пользователь много работает в одном отделе",
            "min_frequency": 5,
            "severity_boost": 0.0,
        },
    }

    def __init__(self, config=None):
        self.config = config or {}
        self.min_frequency = self.config.get("min_frequency", 2)
        self.severity_threshold = self.config.get("severity_threshold", 0.3)

    def detect(self, signals: list) -> list:
        """
        Анализирует сигналы, находит паттерны
        """
        if not signals:
            return []

        patterns = []

        # 1. Группируем по типу
        by_type = defaultdict(list)
        for s in signals:
            by_type[s.type].append(s)

        # 2. Correction loops — поправки с похожим содержимым
        if "correction" in by_type:
            patterns.extend(self._find_correction_loops(by_type["correction"]))

        # 3. Frustration spikes
        if "frustration" in by_type:
            patterns.extend(self._find_frustration_spikes(by_type["frustration"]))

        # 4. Missing knowledge — повторяющиеся запросы
        if "request" in by_type:
            patterns.extend(self._find_missing_knowledge(by_type["request"]))

        # 5. Workflow successes
        if "workflow" in by_type:
            patterns.extend(self._find_workflow_successes(by_type["workflow"]))

        # 6. Unmet needs
        if "unmet" in by_type:
            patterns.extend(self._find_unmet_needs(by_type["unmet"]))

        # 7. Department focus
        patterns.extend(self._find_department_focus(signals))

        return patterns

    def _find_correction_loops(self, signals: list) -> list:
        """Найти циклы поправок — одно и то же исправляется много раз"""
        patterns = []
        
        # Группируем по department
        by_dept = defaultdict(list)
        for s in signals:
            by_dept[s.department].append(s)

        for dept, dept_signals in by_dept.items():
            if len(dept_signals) < self.min_frequency:
                continue

            # Ищем похожие поправки (по ключевым словам)
            word_counts = Counter()
            for s in dept_signals:
                words = set(s.content.lower().split())
                for word in words:
                    if len(word) > 3:  # пропускаем короткие
                        word_counts[word] += 1

            # Слова которые повторяются в поправках
            repeated = [w for w, c in word_counts.items() if c >= self.min_frequency]
            if repeated:
                pattern = Pattern(
                    type="correction_loop",
                    frequency=len(dept_signals),
                    severity=min(0.7 + 0.05 * len(repeated), 1.0),
                    signals=[s.id for s in dept_signals],
                    description=f"Цикл поправок в {dept}: повторяются слова {', '.join(repeated[:5])}",
                    department=dept,
                )
                patterns.append(pattern)

        return patterns

    def _find_frustration_spikes(self, signals: list) -> list:
        """Найти всплески фрустрации"""
        patterns = []
        
        by_dept = defaultdict(list)
        for s in signals:
            by_dept[s.department].append(s)

        for dept, dept_signals in by_dept.items():
            if len(dept_signals) >= 3:
                avg_severity = sum(s.severity for s in dept_signals) / len(dept_signals)
                if avg_severity >= 0.6:
                    pattern = Pattern(
                        type="frustration_spike",
                        frequency=len(dept_signals),
                        severity=avg_severity,
                        signals=[s.id for s in dept_signals],
                        description=f"Всплеск фрустрации в {dept}: {len(dept_signals)} сигналов, средняя серьёзность {avg_severity:.2f}",
                        department=dept,
                    )
                    patterns.append(pattern)

        return patterns

    def _find_missing_knowledge(self, signals: list) -> list:
        """Найти повторяющиеся запросы (недостающие знания).

        Алгоритм: TF-IDF попарное сравнение с порогом cosine > 0.5.
        Лимит: 3 паттерна на департамент, 10 всего.
        """
        patterns = []
        MAX_PER_DEPT = 3
        MAX_TOTAL = 10
        SIMILARITY_THRESHOLD = 0.5

        # Группируем по department
        by_dept = defaultdict(list)
        for s in signals:
            by_dept[s.department].append(s)

        # IDF: чем реже слово, тем оно важнее
        doc_count = len(signals)
        word_doc_freq = Counter()
        for s in signals:
            words = set(s.content.lower().split())
            for w in words:
                word_doc_freq[w] += 1

        for dept, dept_signals in by_dept.items():
            if len(dept_signals) < self.min_frequency:
                continue

            dept_patterns = 0
            word_sets = []
            for s in dept_signals:
                words = set(s.content.lower().split())
                # IDF-взвешенные слова: редкие слова важнее
                weighted = {w: 1.0 / (1.0 + word_doc_freq.get(w, 1))
                           for w in words if len(w) > 3}
                word_sets.append((weighted, s))

            seen_pairs = set()
            for i in range(len(word_sets)):
                if dept_patterns >= MAX_PER_DEPT:
                    break
                for j in range(i + 1, len(word_sets)):
                    if dept_patterns >= MAX_PER_DEPT:
                        break

                    wi, si = word_sets[i]
                    wj, sj = word_sets[j]
                    pair_key = tuple(sorted([si.id, sj.id]))
                    if pair_key in seen_pairs:
                        continue

                    # Cosine similarity на IDF-векторах
                    common_words = set(wi.keys()) & set(wj.keys())
                    if not common_words:
                        continue
                    dot = sum(wi[w] * wj[w] for w in common_words)
                    norm_i = sum(v ** 2 for v in wi.values()) ** 0.5
                    norm_j = sum(v ** 2 for v in wj.values()) ** 0.5
                    if norm_i == 0 or norm_j == 0:
                        continue
                    similarity = dot / (norm_i * norm_j)

                    if similarity >= SIMILARITY_THRESHOLD:
                        important = sorted(common_words,
                                          key=lambda w: wi.get(w, 0) + wj.get(w, 0),
                                          reverse=True)[:5]
                        patterns.append(Pattern(
                            type="missing_knowledge",
                            frequency=2,
                            severity=min(0.3 + similarity * 0.4, 0.9),
                            signals=[si.id, sj.id],
                            description=f"Повторяющийся запрос в {dept} (sim={similarity:.2f}): {', '.join(important)}",
                            department=dept,
                        ))
                        seen_pairs.add(pair_key)
                        dept_patterns += 1

            if patterns and len(patterns) >= MAX_TOTAL:
                break

        return patterns[:MAX_TOTAL]

    def _find_workflow_successes(self, signals: list) -> list:
        """Найти успешные паттерны"""
        patterns = []
        
        by_dept = defaultdict(list)
        for s in signals:
            by_dept[s.department].append(s)

        for dept, dept_signals in by_dept.items():
            if len(dept_signals) >= 2:
                pattern = Pattern(
                    type="workflow_success",
                    frequency=len(dept_signals),
                    severity=0.3,  # позитивный
                    signals=[s.id for s in dept_signals],
                    description=f"Успешный паттерн в {dept}: {len(dept_signals)} подтверждений",
                    department=dept,
                )
                patterns.append(pattern)

        return patterns

    def _find_unmet_needs(self, signals: list) -> list:
        """Найти незакрытые потребности"""
        patterns = []
        
        by_dept = defaultdict(list)
        for s in signals:
            by_dept[s.department].append(s)

        for dept, dept_signals in by_dept.items():
            if len(dept_signals) >= 2:
                pattern = Pattern(
                    type="unmet_need",
                    frequency=len(dept_signals),
                    severity=0.5,
                    signals=[s.id for s in dept_signals],
                    description=f"Незакрытая потребность в {dept}: {len(dept_signals)} запросов",
                    department=dept,
                )
                patterns.append(pattern)

        return patterns

    def _find_department_focus(self, signals: list) -> list:
        """Найти фокус на конкретном отделе"""
        patterns = []
        
        dept_counts = Counter(s.department for s in signals)
        total = len(signals)

        for dept, count in dept_counts.items():
            ratio = count / total if total > 0 else 0
            if count >= 5 and ratio >= 0.3:
                pattern = Pattern(
                    type="department_focus",
                    frequency=count,
                    severity=0.2,
                    signals=[s.id for s in signals if s.department == dept],
                    description=f"Фокус на {dept}: {count} сигналов ({ratio:.0%})",
                    department=dept,
                )
                patterns.append(pattern)

        return patterns
