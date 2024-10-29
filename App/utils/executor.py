from concurrent.futures import ThreadPoolExecutor
import asyncio
import threading


class Executor:
    _executor = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._executor is None:
                cls._executor = ThreadPoolExecutor(max_workers=128)
        return cls._executor