import pytest
import time
from app.metrics.collector import MetricsCollector


class TestMetricsCollector:
    def test_empty_on_init(self):
        c = MetricsCollector(max_samples=10)
        assert c.count == 0
        assert c.get_all() == []
        assert c.get_recent() == []

    def test_record_single(self):
        c = MetricsCollector(max_samples=10)
        c.record(1.0, 50.0, 5.0, 10, 3)
        assert c.count == 1
        assert c.get_all()[0]["speed"] == 50.0

    def test_record_multiple(self):
        c = MetricsCollector(max_samples=100)
        for i in range(5):
            c.record(float(i), float(i * 10), float(i), i, i)
        assert c.count == 5
        assert len(c.get_recent(3)) == 3

    def test_max_samples_respected(self):
        c = MetricsCollector(max_samples=3)
        for i in range(10):
            c.record(float(i), float(i), float(i), i, i)
        assert c.count == 3
        assert c.get_all()[0]["time"] == 7.0

    def test_clear(self):
        c = MetricsCollector(max_samples=10)
        c.record(1.0, 50.0, 5.0, 10, 3)
        c.clear()
        assert c.count == 0

    def test_summary(self):
        c = MetricsCollector(max_samples=100)
        c.record(1.0, 50.0, 5.0, 10, 3)
        c.record(2.0, 60.0, 8.0, 15, 5)
        s = c.summary()
        assert s["speed"]["avg"] == 55.0
        assert s["speed"]["min"] == 50.0
        assert s["speed"]["max"] == 60.0
        assert s["total_samples"] == 2
        assert "wall_time_sec" in s

    def test_summary_empty(self):
        c = MetricsCollector(max_samples=10)
        assert c.summary() == {}

    def test_wall_time(self):
        c = MetricsCollector(max_samples=10)
        assert c.wall_time == 0
        c.record(0, 0, 0, 0, 0)
        assert c.wall_time > 0
