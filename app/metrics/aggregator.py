from statistics import mean, median, stdev


def rolling_avg(data: list[float], window: int = 10) -> list[float]:
    if not data or window < 1:
        return []
    result = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        chunk = data[start:i + 1]
        result.append(sum(chunk) / len(chunk))
    return result


def detect_trend(data: list[float], threshold: float = 0.05) -> str:
    if len(data) < 5:
        return "stable"
    s = _slope(data)
    avg = mean(data) if data else 1
    rel = s / avg if avg != 0 else s
    if rel > threshold:
        return "increasing"
    if rel < -threshold:
        return "decreasing"
    return "stable"


def _slope(data: list[float]) -> float:
    n = len(data)
    if n < 2:
        return 0.0
    xs = list(range(n))
    x_mean = mean(xs)
    y_mean = mean(data)
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, data))
    den = sum((x - x_mean) ** 2 for x in xs)
    return num / den if den != 0 else 0.0


class MetricsAggregator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.speeds = []
        self.waiting_times = []
        self.throughputs = []
        self.queue_lengths = []
        self.fuels = []
        self.co2s = []

    def add_sample(self, speed, waiting_time, throughput, queue_length,
                   fuel=0.0, co2=0.0):
        self.speeds.append(speed)
        self.waiting_times.append(waiting_time)
        self.throughputs.append(throughput)
        self.queue_lengths.append(queue_length)
        self.fuels.append(fuel)
        self.co2s.append(co2)

    def _pct(self, values, p):
        if not values:
            return 0
        s = sorted(values)
        idx = max(0, min(len(s) - 1, int(len(s) * p / 100)))
        return round(s[idx], 2)

    def summary(self):
        def _stats(values):
            if not values:
                return {"min": 0, "max": 0, "avg": 0, "median": 0, "p95": 0, "std": 0}
            return {
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "avg": round(mean(values), 2),
                "median": round(median(values), 2),
                "p95": self._pct(values, 95),
                "std": round(stdev(values), 2) if len(values) > 1 else 0,
            }

        return {
            "speed": _stats(self.speeds),
            "waiting_time": _stats(self.waiting_times),
            "throughput": _stats(self.throughputs),
            "queue_length": _stats(self.queue_lengths),
            "fuel": _stats(self.fuels),
            "co2": _stats(self.co2s),
            "total_samples": len(self.speeds),
        }

    def throughput_rate(self):
        if not self.throughputs:
            return 0
        return sum(self.throughputs) / len(self.throughputs)

    def rolling_speed(self, window=10):
        return rolling_avg(self.speeds, window)

    def trend_speed(self):
        return detect_trend(self.speeds)

    def trend_wait(self):
        return detect_trend(self.waiting_times)

    @staticmethod
    def compare_runs(aggregators):
        results = []
        for i, agg in enumerate(aggregators):
            s = agg.summary()
            results.append({
                "run": i + 1,
                "avg_speed": s["speed"]["avg"],
                "avg_wait": s["waiting_time"]["avg"],
                "total_throughput": sum(agg.throughputs) if agg.throughputs else 0,
                "samples": s["total_samples"],
            })
        return results
