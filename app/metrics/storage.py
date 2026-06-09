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
        return self._local.conn

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                algorithm TEXT,
                flow_rate INTEGER,
                total_steps INTEGER
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
                FOREIGN KEY (run_id) REFERENCES simulation_runs(id)
            )
        """)
        conn.commit()
        conn.close()

    def create_run(self, algorithm, flow_rate):
        cur = self.conn.execute(
            "INSERT INTO simulation_runs (start_time, algorithm, flow_rate) VALUES (?, ?, ?)",
            (datetime.now().isoformat(), algorithm, flow_rate),
        )
        self.conn.commit()
        return cur.lastrowid

    def save_samples(self, run_id, samples):
        self.conn.executemany(
            "INSERT INTO metrics_samples (run_id, time_step, avg_speed, avg_waiting_time, throughput, queue_length) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (run_id, s["time"], s["speed"], s["waiting_time"], s["throughput"], s["queue_length"])
                for s in samples
            ],
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

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
