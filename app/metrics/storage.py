import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path


class MetricsStorage:
    def __init__(self, db_path="data/metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_db()

    @property
    def conn(self):
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(str(self.db_path))
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
        return self._local.conn

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                algorithm TEXT,
                flow_rate INTEGER,
                total_steps INTEGER,
                map_name TEXT DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                time_step REAL NOT NULL,
                avg_speed REAL,
                avg_waiting_time REAL,
                throughput INTEGER,
                queue_length INTEGER,
                fuel REAL DEFAULT 0,
                co2 REAL DEFAULT 0,
                FOREIGN KEY (run_id) REFERENCES simulation_runs(id)
            )
        """)
        # Migrate existing tables if columns missing
        try:
            conn.execute("ALTER TABLE metrics_samples ADD COLUMN fuel REAL DEFAULT 0")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE metrics_samples ADD COLUMN co2 REAL DEFAULT 0")
        except Exception:
            pass
        conn.commit()
        conn.close()

    def create_run(self, algorithm, flow_rate, map_name=""):
        cur = self.conn.execute(
            "INSERT INTO simulation_runs (start_time, algorithm, flow_rate, map_name) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(), algorithm, flow_rate, map_name),
        )
        self.conn.commit()
        return cur.lastrowid

    def save_samples(self, run_id, samples):
        if not samples:
            return
        data = [
            (
                run_id, s["time"], s["speed"], s["waiting_time"],
                s["throughput"], s["queue_length"],
                s.get("fuel", 0), s.get("co2", 0),
            )
            for s in samples
        ]
        self.conn.executemany(
            "INSERT INTO metrics_samples (run_id, time_step, avg_speed, avg_waiting_time, throughput, queue_length, fuel, co2) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            data,
        )
        self.conn.commit()

    def end_run(self, run_id, total_steps):
        self.conn.execute(
            "UPDATE simulation_runs SET end_time = ?, total_steps = ? WHERE id = ?",
            (datetime.now().isoformat(), total_steps, run_id),
        )
        self.conn.commit()

    def get_runs(self, limit=20):
        cur = self.conn.execute(
            "SELECT * FROM simulation_runs ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cur.fetchall()]

    def get_run_samples(self, run_id):
        cur = self.conn.execute(
            "SELECT * FROM metrics_samples WHERE run_id = ? ORDER BY time_step", (run_id,)
        )
        return [dict(row) for row in cur.fetchall()]

    def delete_run(self, run_id):
        self.conn.execute("DELETE FROM metrics_samples WHERE run_id = ?", (run_id,))
        self.conn.execute("DELETE FROM simulation_runs WHERE id = ?", (run_id,))
        self.conn.commit()

    def export_json(self, run_id, filepath):
        run = self.conn.execute(
            "SELECT * FROM simulation_runs WHERE id = ?", (run_id,)
        ).fetchone()
        if not run:
            raise ValueError(f"Run {run_id} not found")
        samples = self.get_run_samples(run_id)
        data = {"run": dict(run), "samples": samples}
        Path(filepath).write_text(json.dumps(data, indent=2))
        return filepath

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
