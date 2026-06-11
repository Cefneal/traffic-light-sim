# Project Structure

Berikut struktur lengkap proyek TLS (Traffic Light Simulation).

```
traffic-light-sim/
│
├── app/                           # Kode utama aplikasi
│   ├── __init__.py                # Package marker
│   ├── main.py                    # Entry point: init config, logger, MainWindow, SimController
│   │
│   ├── engine/                    # ⚙️ P1 — Simulation Engine
│   │   ├── __init__.py
│   │   ├── sim_controller.py      # Lifecycle SUMO: start/stop/pause/resume, TL algorithm dispatch
│   │   ├── traci_client.py        # Wrapper TraCI: vehicles, traffic lights, edges, detectors
│   │   ├── tl_algorithms.py       # TL controllers: fixed, actuated, max_pressure, green_wave
│   │   └── osm_importer.py        # OSM → SUMO converter via netconvert
│   │
│   ├── gui/                       # 🖥️ P3 — Graphical User Interface
│   │   ├── __init__.py
│   │   ├── main_window.py         # Top-level window: menu, splitter, signal bridge for thread safety
│   │   ├── map_viewer.py          # QGraphicsView: render roads, vehicles, traffic lights (3-circle)
│   │   ├── dashboard.py           # pyqtgraph charts: speed, wait, throughput, queue
│   │   ├── controls.py            # Toolbar: Play/Pause/Stop/Step + map dropdown + speed slider
│   │   ├── config_panel.py        # Sidebar: TL algorithm, cycle time, flow rate, heatmap toggle
│   │   ├── scenario_dialog.py     # New/Open/Save scenario (persisted to ~/.tls/scenarios/*.json)
│   │   └── settings_dialog.py     # Preferences: language, SUMO path, DB path
│   │
│   ├── metrics/                   # 📊 P2 — Metrics & Storage
│   │   ├── __init__.py
│   │   ├── collector.py           # In-memory sample collector (deque, max 7200 samples)
│   │   ├── storage.py             # SQLite storage: simulation_runs + metrics_samples tables
│   │   └── aggregator.py          # Statistical aggregation: mean, median, p95, stdev, compare_runs
│   │
│   ├── models/                    # 📦 Data Models
│   │   ├── traffic_light.py       # TrafficLight, TLPhase, TLState, TLAlgorithm (dataclass)
│   │   ├── vehicle.py             # Vehicle dataclass (id, type, pos, speed, angle, waiting_time)
│   │   ├── network.py             # RoadNetwork, Node, Edge, Lane, TrafficLightLogic (unused)
│   │   └── scenario.py            # Scenario config / generate_sumo_config (unused)
│   │
│   └── utils/                     # 🛠️ P2 — Utilities
│       ├── __init__.py
│       ├── config.py              # Config from ~/.tls/config.json + env overrides
│       ├── logger.py              # Logging: console + rotating file (5MB×3) + exception hook
│       └── localization.py        # i18n: t() function with dot-notation, EN/ID locale files
│
├── sim/                           # 🗺️ Simulation Data (1 folder per map)
│   ├── pamulang/                  # Pamulang, Tangerang Selatan — 36 TL, ~1800 vehicles
│   │   ├── network.net.xml        #   SUMO road network
│   │   ├── routes.xml             #   Vehicle routes (car 55%, motor 25%, truck 8%, bus 5%, angkot 7%)
│   │   └── test.sumocfg           #   Simulation config (1800s, teleport 120s)
│   ├── silicon_valley/            # (setup by scripts/siapkan_map.sh)
│   └── tokyo/                     # (setup by scripts/siapkan_map.sh)
│
├── scripts/                       # 📜 Utility Scripts
│   ├── siapkan_map.sh             # One-step OSM → SUMO pipeline
│   └── setup_all_maps.sh          # Download + convert all preset maps
│
├── docs/                          # 📖 Documentation
│   ├── panduan-penggunaan.html    # Full usage guide (Indonesia+English) — 11 chapters
│   ├── panduan-penggunaan.pdf     # PDF version
│   ├── audit-laporan.html         # Complete audit report
│   └── audit-laporan.pdf          # PDF version
│
├── tests/                         # 🧪 Unit Tests (33 passing)
│   ├── test_config.py             # Config: defaults, env override, db path expansion
│   ├── test_logger.py             # Logger: creation, same-name return, file output
│   ├── test_collector.py          # Collector: record, max_samples, clear, summary, wall_time
│   ├── test_storage.py            # Storage: CRUD, export JSON, delete run
│   └── test_aggregator.py         # Aggregator: stats, compare_runs, percentiles
│
├── resources/
│   └── locales/                   # i18n files
│       ├── id_ID.json             # Indonesian
│       └── en_US.json             # English
│
├── logs/                          # Runtime logs (auto-rotated, 5MB×3)
├── sumo_bin/                      # Bundled SUMO binaries (optional)
│
├── requirements.txt               # Python dependencies
├── setup.sh                       # One-step install script
├── pytest.ini                     # Pytest config
├── README.md                      # This file
└── PROJECT_STRUCTURE.md           # This file
```

## Dependency Flow

```
  User klik Play
       │
       ▼
  ControlsToolbar ──► SimController.start() ──► spawn SUMO process
       │                                              │
       │                                              ▼
       │                                        TraCIClient.connect()
       │                                              │
       │                                              ▼
       │                                   _build_traffic_lights()
       │                                              │
       │                                              ▼
       │                                   _run_loop() [daemon thread]
       │                                        │
       │                                        ├── traci.simulationStep()
       │                                        ├── MetricsCollector.record()
       │                                        ├── TL algorithm dispatch
       │                                        │     └── get_controller(name)(tl, traci, time, step)
       │                                        └── emit "step" signal
       │                                              │
       │                                              ▼
       │                                   MainWindow._on_step_data() [main thread]
       │                                              │
       │                                              ▼
       │                                   DashboardPanel.add_data_point()
       │                                        │
       │                                        ▼ (when stop)
       │                                   MetricsStorage.save_samples()
       │
  ConfigPanel ──► signal config_applied ──► SimController.set_algorithm()
  MapViewer    ◄── TraCIClient.get_tl_state() / get_vehicle_ids()
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Signal bridge untuk thread safety | Qt widgets must only be modified from main thread; sim runs in daemon thread |
| TraCIClient wrapper + raw traci for algorithms | Wrapper = convenience; algorithms need raw traci for low-level TL control |
| Metrics disimpan pas stop, bukan per-step | Batch insert lebih efisien, gak bebanin loop |
| Config persisted di ~/.tls/config.json | Portable antar session, bisa di-edit manual |
| Map selector dropdown + Browse | User bisa pilih preset map atau custom .sumocfg |

## Scoring (per Role)

| Role | Files | LOC (approx) | Responsibility |
|------|-------|-------------|----------------|
| **P1** ⚙️ Engine | 4 | 500 | TraCIClient, sim_controller, tl_algorithms, osm_importer |
| **P2** 📊 Backend | 7 | 600 | config, logger, localization, collector, storage, aggregator, main.py |
| **P3** 🖥️ GUI | 8 | 1000 | main_window, map_viewer, dashboard, controls, config_panel, dialogs |
| **Tests** 🧪 | 5 | 250 | 33 unit tests, all passing |
