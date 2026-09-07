import time
from collections import defaultdict, deque
from threading import Lock


class RateLimiter:
    def __init__(self, limit: int = 5, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
        self.lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()

        with self.lock:
            queue = self.requests[key]

            while queue and now - queue[0] > self.window_seconds:
                queue.popleft()

            if len(queue) >= self.limit:
                return False

            queue.append(now)
            return True


ip_limiter = RateLimiter(limit=5, window_seconds=60)
widget_limiter = RateLimiter(limit=10, window_seconds=60)