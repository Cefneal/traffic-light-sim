from statistics import mean, median, stdev


class MetricsAggregator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.speeds = []
        self.waiting_times = []
        self.throughputs = []
        self.queue_lengths = []

    def add_sample(self, speed, waiting_time, throughput, queue_length):
        self.speeds.append(speed)
        self.waiting_times.append(waiting_time)
        self.throughputs.append(throughput)
        self.queue_lengths.append(queue_length)

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
            "total_samples": len(self.speeds),
        }

    def throughput_rate(self):
        if not self.throughputs:
            return 0
        return sum(self.throughputs) / len(self.throughputs)

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
