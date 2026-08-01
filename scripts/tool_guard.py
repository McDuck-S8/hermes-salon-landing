
# Unified Tool Error Recovery
import functools
import time

def with_recovery(fallback=None, max_retries=2, backoff=1.0):
    """Decorator: retry with exponential backoff, then fallback."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        time.sleep(backoff * (2 ** attempt))
            # Все попытки исчерпаны
            if fallback:
                return fallback(*args, **kwargs)
            raise last_error
        return wrapper
    return decorator
