"""
Bayesian Decision Scorer — замена линейной формулы.
P(success | action, context) с учётом похожести контекстов.
"""

import math
from datetime import datetime
from typing import Dict, Any, Optional


class BayesianScorer:
    """
    Вычисляет score действия на основе байесовской оценки
    вероятности успеха в данном контексте.
    
    Использует Beta-распределение:
    - Среднее: α/(α+β) — ожидаемая вероятность успеха
    - Дисперсия: exploration bonus для непроверенных действий
    """
    
    def __init__(self, feedback_store):
        self.feedback = feedback_store
        self.prior_alpha = 1.0  # Beta(1,1) — равномерное prior
        self.prior_beta = 1.0
    
    def compute_score(self, action, context: Dict[str, Any]) -> float:
        """
        Вычисляет score для action в данном контексте.
        
        Выше score = выше вероятность что действие будет успешным.
        Учитывает:
        - Историю исходов этого типа действий
        - Похожесть контекстов (блокированная сеть, время суток, etc.)
        - Давность исходов (недавние важнее)
        - Exploration bonus (непроверенные действия получают шанс)
        """
        history = self.feedback.get_by_type(action.type)
        
        if not history:
            # Нет данных — равномерное prior + высокий exploration
            return 0.5 + self._exploration_bonus(self.prior_alpha, self.prior_beta)
        
        weighted_successes = 0.0
        weighted_failures = 0.0
        
        for entry in history:
            # Насколько контекст входа похож на текущий
            similarity = self._context_similarity(context, entry.get('context', {}))
            
            # Насколько давно был исход (недельный период полураспада)
            recency = self._time_decay(entry.get('timestamp'))
            
            weight = similarity * recency
            
            if entry.get('outcome', 0) > 0:
                weighted_successes += weight
            else:
                weighted_failures += weight * abs(entry.get('outcome', 0))
        
        # Байесовское обновление
        alpha = self.prior_alpha + weighted_successes
        beta = self.prior_beta + weighted_failures
        
        # Expected success rate
        expected = alpha / (alpha + beta)
        
        # Exploration bonus: дисперсия Beta-распределения
        exploration = self._exploration_bonus(alpha, beta)
        
        return expected + exploration
    
    def _context_similarity(self, ctx1: Dict, ctx2) -> float:
        """
        Насколько похожи два контекста.
        Возвращает 0 (совсем разные) до 1 (идентичны).
        ctx2 может быть строкой (из feedback) или dict.
        """
        # If ctx2 is a string, try to parse as dict or return partial match
        if isinstance(ctx2, str):
            if not ctx2:
                return 0.5  # Empty string — unknown context
            # String context — check if keywords match
            return 0.5  # Default for string contexts
        
        if not ctx1 or not ctx2:
            return 0.5  # Нет данных о контексте — среднее
        
        dimensions = {
            'network_status': 0.35,   # Самое важное: blocked/available
            'environment': 0.25,      # cloud/local
            'error_state': 0.25,      # normal/degraded/error
            'time_of_day': 0.10,      # утро/день/вечер/ночь
            'load': 0.05,            # низкая/средняя/высокая нагрузка
        }
        
        total_weight = 0.0
        match_weight = 0.0
        
        for dim, weight in dimensions.items():
            total_weight += weight
            val1 = ctx1.get(dim)
            val2 = ctx2.get(dim)
            
            if val1 is not None and val2 is not None:
                if val1 == val2:
                    match_weight += weight
                # Частичное совпадение для близких значений
                elif dim == 'time_of_day':
                    # Утро похоже на день (соседние периоды)
                    periods = ['morning', 'afternoon', 'evening', 'night']
                    if val1 in periods and val2 in periods:
                        dist = abs(periods.index(val1) - periods.index(val2))
                        if dist == 1:
                            match_weight += weight * 0.5
        
        return match_weight / total_weight if total_weight > 0 else 0.5
    
    def _time_decay(self, timestamp) -> float:
        """
        Экспоненциальное затухание.
        Период полураспада: 7 дней.
        Исход сегодня = вес 1.0
        Исход неделю назад = вес 0.5
        Исход месяц назад = вес ~0.06
        """
        if timestamp is None:
            return 0.5
        
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except ValueError:
                return 0.5
        
        age_hours = (datetime.now() - timestamp).total_seconds() / 3600
        half_life_hours = 168  # 7 дней
        
        return math.exp(-age_hours * math.log(2) / half_life_hours)
    
    def _exploration_bonus(self, alpha: float, beta: float) -> float:
        """
        Дисперсия Beta-распределения.
        Высокая когда мало данных (нужно исследовать).
        Низкая когда много данных (можно использовать).
        """
        total = alpha + beta
        variance = (alpha * beta) / (total * total * (total + 1))
        return variance * 2.0  # Масштабируем для видимого эффекта
    
    def get_confidence(self, action, context: Dict[str, Any]) -> float:
        """
        Насколько мы уверены в оценке для этого действия.
        0 = полная неуверенность, 1 = абсолютная уверенность.
        Используется для принятия решения: действовать или спросить пользователя.
        """
        history = self.feedback.get_by_type(action.type)
        
        if not history:
            return 0.0
        
        # Количество эффективных наблюдений (с учётом затухания)
        effective_n = sum(self._time_decay(e.get('timestamp')) for e in history)
        
        # Уверенность растёт с числом наблюдений, но никогда не 100%
        return 1.0 - 1.0 / (1.0 + effective_n / 10.0)
