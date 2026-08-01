#!/usr/bin/env python3
"""
Config Guard — валидация конфигурации и pre-checks для доменных операций.
Помогает с domain_failure_pattern (7 фиксов) и log_unknown.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional


CONFIG_PATH = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes")) / "config.yaml"


class ConfigGuard:
    """Валидация конфигурации и предварительные проверки."""
    
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self._config = None
    
    def load(self) -> Dict[str, Any]:
        """Загрузить конфиг с валидацией."""
        if self._config is not None:
            return self._config
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}
        
        return self._config
    
    def validate(self) -> List[str]:
        """Проверить конфиг на критичные проблемы. Возвращает список ошибок."""
        errors = []
        cfg = self.load()
        
        # Обязательные секции
        required_sections = ['delegation', 'cron', 'providers']
        for section in required_sections:
            if section not in cfg:
                errors.append(f"Missing required section: {section}")
        
        # Проверка провайдеров
        if 'providers' in cfg:
            for name, prov in cfg['providers'].items():
                if 'model' not in prov:
                    errors.append(f"Provider '{name}' missing 'model'")
                if 'provider' not in prov:
                    errors.append(f"Provider '{name}' missing 'provider' field")
        
        # Проверка крона
        if 'cron' in cfg:
            jobs = cfg['cron'].get('jobs', [])
            for job in jobs:
                if not job.get('id'):
                    errors.append("Cron job missing 'id'")
                if not job.get('script') and not job.get('prompt'):
                    errors.append(f"Job {job.get('id', '?')} missing script/prompt")
        
        return errors
    
    def get(self, key: str, default: Any = None) -> Any:
        """Безопасное получение значения с точечной нотацией: 'providers.openrouter.model'."""
        cfg = self.load()
        parts = key.split('.')
        val = cfg
        for part in parts:
            if isinstance(val, dict):
                val = val.get(part)
            else:
                return default
            if val is None:
                return default
        return val
    
    def set(self, key: str, value: Any) -> None:
        """Установить значение и сохранить."""
        cfg = self.load()
        parts = key.split('.')
        target = cfg
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = value
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
        
        self._config = cfg
    
    def ensure_domain_config(self, domain: str) -> Dict[str, Any]:
        """Убедиться, что для домена есть базовая конфигурация."""
        domain_key = f"domains.{domain}"
        if self.get(domain_key) is None:
            default = {
                "enabled": True,
                "retry_count": 3,
                "timeout": 30,
                "circuit_breaker": True,
            }
            self.set(domain_key, default)
            return default
        return self.get(domain_key)


# Глобальный экземпляр
CONFIG_GUARD = ConfigGuard()


def validate_config() -> bool:
    """Проверить конфиг, выбросить исключение если критично."""
    errors = CONFIG_GUARD.validate()
    if errors:
        raise ValueError(f"Config validation failed: {'; '.join(errors)}")
    return True


def get_domain_config(domain: str) -> Dict[str, Any]:
    """Получить конфиг домена с дефолтами."""
    return CONFIG_GUARD.ensure_domain_config(domain)




# High-risk домены (из self_improvement_loop)
HIGH_RISK_DOMAINS = {
    "advanced-analytics": {"failure_rate": 1.0, "min_entries": 5},
    "ai-content-factory": {"failure_rate": 1.0, "min_entries": 5},
    "architecture": {"failure_rate": 1.0, "min_entries": 5},
    "b2b-sales": {"failure_rate": 1.0, "min_entries": 5},
    "behavioral-psychology": {"failure_rate": 1.0, "min_entries": 5},
    "browser": {"failure_rate": 1.0, "min_entries": 5},
    "bugfix": {"failure_rate": 1.0, "min_entries": 5},
}

def is_high_risk_domain(domain: str) -> bool:
    """
    Проверить, является ли домен высокорисковым.
    """
    return domain in HIGH_RISK_DOMAINS

if __name__ == "__main__":
    try:
        validate_config()
        print("✅ Config validation passed")
    except ValueError as e:
        print(f"❌ Config validation failed: {e}")