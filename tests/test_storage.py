import pytest
import tempfile
from pathlib import Path
from app.metrics.storage import MetricsStorage


class TestMetricsStorage:
    @pytest.fixture
    def storage(self, tmp_path):
        db_path = str(tmp_path / "test_metrics.db")
        s = MetricsStorage(db_path=db_path)
        yield s
        s.close()

    def test_create_run(self, storage):
        run_id = storage.create_run("fixed", 500)
        assert run_id is not None
        assert isinstance(run_id, int)
        assert run_id > 0

    def test_create_run_with_map(self, storage):
        run_id = storage.create_run("actuated", 1000, map_name="pamulang")
        assert run_id > 0

    def test_save_and_get_samples(self, storage):
        run_id = storage.create_run("fixed", 500)
        samples = [{"time": 1.0, "speed": 50, "waiting_time": 5, "throughput": 10, "queue_length": 3}]
        storage.save_samples(run_id, samples)
        result = storage.get_run_samples(run_id)
        assert len(result) == 1
        assert result[0]["avg_speed"] == 50
        assert result[0]["time_step"] == 1.0

    def test_empty_samples_no_error(self, storage):
        run_id = storage.create_run("fixed", 500)
        storage.save_samples(run_id, [])  # should not raise

    def test_end_run(self, storage):
        run_id = storage.create_run("fixed", 500)
        storage.end_run(run_id, 100)
        runs = storage.get_runs()
        assert runs[0]["total_steps"] == 100
        assert runs[0]["end_time"] is not None

    def test_get_runs_empty(self, storage):
        assert storage.get_runs() == []

    def test_get_runs_order(self, storage):
        r1 = storage.create_run("a", 100)
        r2 = storage.create_run("b", 200)
        runs = storage.get_runs(limit=10)
        assert runs[0]["id"] == r2  # newest first

    def test_delete_run(self, storage):
        run_id = storage.create_run("fixed", 500)
        storage.save_samples(run_id, [{"time": 1.0, "speed": 50, "waiting_time": 5, "throughput": 10, "queue_length": 3}])
        storage.delete_run(run_id)
        assert storage.get_run_samples(run_id) == []
        runs = storage.get_runs()
        assert all(r["id"] != run_id for r in runs)

    def test_export_json(self, storage, tmp_path):
        run_id = storage.create_run("fixed", 500)
        storage.save_samples(run_id, [{"time": 1.0, "speed": 50, "waiting_time": 5, "throughput": 10, "queue_length": 3}])
        out = str(tmp_path / "export.json")
        result = storage.export_json(run_id, out)
        assert Path(result).exists()
        import json
        data = json.loads(Path(result).read_text())
        assert "run" in data
        assert "samples" in data
