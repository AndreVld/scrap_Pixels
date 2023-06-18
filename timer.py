from time import time
from typing import Callable, Any


def async_timed(func: Callable) -> Callable:
    async def wrapper(*args, **kwargs) -> Any:
        start = time()
        try:
            return await func(*args, **kwargs)
        finally:
            total = time() - start
            print(f'"{func.__name__}" completed in {total:.2f} seconds')
    return wrapper