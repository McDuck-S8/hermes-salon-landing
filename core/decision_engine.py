"""
Decision Engine — wraps BayesianScorer for autonomous_agent.
Provides compute_score() and context collection.
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from core.bayesian_scorer import BayesianScorer


class DecisionEngine:
    """Wraps BayesianScorer with context collection for autonomous_agent."""
    
    def __init__(self, feedback_store):
        self.bayesian = BayesianScorer(feedback_store)
    
    def compute_score(self, action, context=None):
        """
        Байесовская оценка вероятности успеха действия в данном контексте.
        Заменяет старую линейную формулу.
        """
        if context is None:
            context = self._get_current_context()
        
        # Байесовский score
        bayesian_score = self.bayesian.compute_score(action, context)
        
        # SELF-ASK: перед принятием решения
        try:
            from core.self_ask import self_ask_before_action
            answers = self_ask_before_action(action, context)
            
            # Если обслуживание и нет необходимости — снижаем score
            if (answers.get("infrastructure_or_result") == "infrastructure" and
                answers.get("infrastructure_needed_now") == "no"):
                bayesian_score *= 0.3  # Штраф за infrastructure без необходимости
            
            # Если score и importance не совпадают — снижаем
            if answers.get("score_vs_importance") == "misaligned":
                bayesian_score *= 0.7
        except ImportError:
            pass
        
        # Сохраняем уверенность для возможной эскалации
        confidence = self.bayesian.get_confidence(action, context)
        
        # Если уверенность слишком низкая — снижаем score
        if confidence < 0.2:
            bayesian_score *= (0.5 + confidence)
        
        return bayesian_score
    
    def _get_current_context(self):
        """Собирает текущий контекст для байесовского скорера."""
        return {
            'time_of_day': self._get_time_of_day(),
            'network_status': self._get_network_status(),
            'environment': self._get_environment(),
            'error_state': self._get_error_state(),
        }
    
    def _get_time_of_day(self):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def _get_network_status(self):
        try:
            import urllib.request
            req = urllib.request.Request("https://httpbin.org/get", headers={"User-Agent": "Mozilla/5.0"})
            urllib.request.urlopen(req, timeout=3)
            return 'available'
        except Exception:
            return 'blocked'
    
    def _get_environment(self):
        try:
            import socket
            hostname = socket.gethostname()
            if 'cloud' in hostname.lower() or 'aws' in hostname.lower():
                return 'cloud'
            return 'local'
        except:
            return 'unknown'
    
    def _get_error_state(self):
        try:
            error_log = Path(__file__).resolve().parent.parent / "logs" / "errors.log"
            if error_log.exists():
                mtime = datetime.fromtimestamp(error_log.stat().st_mtime)
                age_minutes = (datetime.now() - mtime).total_seconds() / 60
                if age_minutes < 30:
                    return 'error'
                elif age_minutes < 120:
                    return 'degraded'
            return 'normal'
        except:
            return 'unknown'


# Singleton instance
_engine = None

def get_decision_engine(feedback_store=None):
    global _engine
    if _engine is None:
        if feedback_store is None:
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
            from feedback_store import load_feedback
            # Create a simple wrapper that matches what BayesianScorer expects
            class SimpleFeedback:
                def __init__(self):
                    self.entries = load_feedback()
                def get_by_type(self, action_type):
                    return [e for e in self.entries if e.get("action_id", "").startswith(action_type)]
            feedback_store = SimpleFeedback()
        _engine = DecisionEngine(feedback_store)
    return _engine
