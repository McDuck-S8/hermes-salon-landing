#!/usr/bin/env python3
"""
Circuit Breaker для сетевых вызовов (httpx, telegram, tavily).
Предотвращает каскадные ошибки при недоступности сервисов.
"""

import time
from functools import wraps
from typing import Callable, Any


class CircuitBreaker:
    """Circuit Breaker pattern для защиты от каскадных сбоев."""
    
    def __init__(
        self, 
        failure_threshold: int = 3, 
        timeout: int = 30,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failures = 0
        self.last_failure = 0
        self.open = False
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.open:
            if time.time() - self.last_failure > self.timeout:
                self.open = False
                self.failures = 0
            else:
                raise Exception("Circuit breaker OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self.failures = 0
            return result
        except self.expected_exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.failure_threshold:
                self.open = True
            raise


# Глобальные брейкеры для основных сервисов
TELEGRAM_BREAKER = CircuitBreaker(failure_threshold=3, timeout=30)
HTTPX_BREAKER = CircuitBreaker(failure_threshold=3, timeout=30)
TAVILY_BREAKER = CircuitBreaker(failure_threshold=3, timeout=30)


def with_circuit_breaker(breaker: CircuitBreaker = None):
    """Декоратор: автоматический circuit breaker для функции."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            brk = breaker or HTTPX_BREAKER
            return brk.call(func, *args, **kwargs)
        return wrapper
    return decorator


# Удобные декораторы для конкретных сервисов
def with_telegram_breaker(func: Callable) -> Callable:
    return with_circuit_breaker(TELEGRAM_BREAKER)(func)

def with_httpx_breaker(func: Callable) -> Callable:
    return with_circuit_breaker(HTTPX_BREAKER)(func)

def with_tavily_breaker(func: Callable) -> Callable:
    return with_circuit_breaker(TAVILY_BREAKER)(func)