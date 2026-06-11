import pytest
from app.metrics.aggregator import MetricsAggregator


class TestMetricsAggregator:
    def test_empty_on_init(self):
        agg = MetricsAggregator()
        s = agg.summary()
        assert s["total_samples"] == 0
        assert s["speed"]["min"] == 0

    def test_add_sample(self):
        agg = MetricsAggregator()
        agg.add_sample(50.0, 5.0, 10, 3)
        assert agg.summary()["total_samples"] == 1

    def test_summary_values(self):
        agg = MetricsAggregator()
        agg.add_sample(50.0, 5.0, 10, 3)
        agg.add_sample(60.0, 8.0, 15, 5)
        s = agg.summary()
        assert s["speed"]["avg"] == 55.0
        assert s["speed"]["min"] == 50.0
        assert s["speed"]["max"] == 60.0
        assert s["waiting_time"]["avg"] == 6.5
        assert s["throughput"]["avg"] == 12.5
        assert s["queue_length"]["avg"] == 4.0

    def test_reset(self):
        agg = MetricsAggregator()
        agg.add_sample(50.0, 5.0, 10, 3)
        agg.reset()
        assert agg.summary()["total_samples"] == 0

    def test_throughput_rate(self):
        agg = MetricsAggregator()
        assert agg.throughput_rate() == 0
        agg.add_sample(50.0, 5.0, 10, 3)
        agg.add_sample(60.0, 8.0, 20, 5)
        assert agg.throughput_rate() == 15.0

    def test_median_and_p95(self):
        agg = MetricsAggregator()
        for v in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            agg.add_sample(float(v), float(v), int(v), int(v))
        s = agg.summary()
        assert s["speed"]["median"] == 55.0
        assert s["speed"]["p95"] == 100.0  # 95th pct of 10 vals sorted = highest

    def test_compare_runs(self):
        a1 = MetricsAggregator()
        a1.add_sample(50.0, 5.0, 10, 3)
        a2 = MetricsAggregator()
        a2.add_sample(60.0, 8.0, 15, 5)
        result = MetricsAggregator.compare_runs([a1, a2])
        assert len(result) == 2
        assert result[0]["run"] == 1
        assert result[1]["run"] == 2
        assert result[0]["avg_speed"] == 50.0
        assert result[1]["avg_speed"] == 60.0
