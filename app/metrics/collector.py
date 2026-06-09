import time
from collections import deque

from app.utils.logger import get_logger


class MetricsCollector:
    def __init__(self, max_samples=3600):
        self.logger = get_logger("metrics")
        self.max_samples = max_samples
        self.samples = deque(maxlen=max_samples)
        self._start_time = None

    def record(self, time_step, speed, waiting_time, throughput, queue_length):
        self.samples.append({
            "time": time_step,
            "speed": speed,
            "waiting_time": waiting_time,
            "throughput": throughput,
            "queue_length": queue_length,
        })
        if self._start_time is None:
            self._start_time = time.time()

    def get_recent(self, n=100):
        return list(self.samples)[-n:]

    def get_all(self):
        return list(self.samples)

    def clear(self):
        self.samples.clear()
        self._start_time = None

    @property
    def count(self):
        return len(self.samples)
