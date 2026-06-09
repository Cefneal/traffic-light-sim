import time
from collections import deque
from statistics import mean, stdev

from app.utils.logger import get_logger


class MetricsCollector:
    def __init__(self, max_samples=3600):
        self.logger = get_logger("metrics")
        self.max_samples = max_samples
        self.samples = deque(maxlen=max_samples)
        self._start_time = None

    def record(self, time_step, speed, waiting_time, throughput, queue_length):
        elapsed = None
        if self._start_time is not None:
            elapsed = time.time() - self._start_time

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
        self.logger.info("Metrics collector cleared")

    @property
    def count(self):
        return len(self.samples)

    @property
    def wall_time(self):
        if self._start_time is None:
            return 0
        return time.time() - self._start_time

    def summary(self):
        if not self.samples:
            return {}

        speeds = [s["speed"] for s in self.samples]
        waits = [s["waiting_time"] for s in self.samples]
        tputs = [s["throughput"] for s in self.samples]
        queues = [s["queue_length"] for s in self.samples]

        def _stats(vals):
            if not vals:
                return {"min": 0, "max": 0, "avg": 0}
            return {
                "min": round(min(vals), 2),
                "max": round(max(vals), 2),
                "avg": round(mean(vals), 2),
            }

        return {
            "speed": _stats(speeds),
            "waiting_time": _stats(waits),
            "throughput": _stats(tputs),
            "queue_length": _stats(queues),
            "total_samples": len(self.samples),
            "wall_time_sec": round(self.wall_time, 2),
        }
