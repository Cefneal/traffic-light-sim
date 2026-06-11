# TLS — Traffic Light Simulation

Aplikasi desktop simulasi lalu lintas skala kota dengan **SUMO engine** + **Python PyQt6**.

## Fitur

- **3 map preset**: Pamulang, Silicon Valley, Tokyo — masing-masing dgn lampu merah & kendaraan realistis
- **4 algoritma TL**: Fixed-Time, Actuated, Green Wave, Max-Pressure
- **Dashboard real-time**: Grafik kecepatan rata-rata, waktu tunggu, throughput, antrian
- **Import OSM**: Download dari OpenStreetMap → langsung bisa simulate
- **Multi-platform**: Linux & Windows

## Instalasi

### 1. Install SUMO

**Linux (Ubuntu/Debian):**
```bash
sudo apt install sumo sumo-tools
```

**Windows:**
Download installer dari https://sumo.dlr.de/docs/Downloads.php (pilih `sumo-1.20.0.msi` atau versi terbaru).
Pastikan SUMO binary sudah ada di PATH (bisa diatur via menu File > Settings).

### 2. Clone repo & setup

```bash
git clone https://github.com/Cefneal/traffic-light-sim.git
cd traffic-light-sim
bash setup.sh
```

Atau manual:
```bash
cd traffic-light-sim
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Jalankan

```bash
python -m app.main
```

## Cara Pakai

1. Pilih map dari dropdown di toolbar (Pamulang / Silicon Valley / Tokyo)
2. Atur algoritma TL di panel Configuration (Fixed-Time / Actuated / Green Wave)
3. Klik **▶ Play** — simulation berjalan
4. Lihat dashboard real-time di panel kanan
5. Export data CSV/JSON via menu File

### Map Custom

1. Download OSM dari https://www.openstreetmap.org/export
2. Buka app → File → Import OSM → pilih file .osm
3. Atau: `bash scripts/siapkan_map.sh /path/map.osm`

## Struktur Proyek

```
app/                    Kode utama aplikasi
├── main.py             Entry point
├── engine/             Engine (P1): TraCI client, TL algorithms, OSM importer
├── gui/                GUI (P3): main window, map viewer, dashboard, controls
├── metrics/            Metrics (P2): collector, storage SQLite, aggregator
├── models/             Data models: traffic light, vehicle, network, scenario
└── utils/              Utilities (P2): config, logger, localization
sim/                    Data simulasi (map per folder)
docs/                   Dokumentasi
scripts/                Script utilitas
tests/                  Unit tests
```

## Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| GUI | PyQt6 |
| Charts | pyqtgraph |
| Engine | SUMO (via TraCI) |
| Database | SQLite |
| Report | weasyprint |

## Troubleshooting

| Problem | Solusi |
|---------|--------|
| `SUMO not found` | Install SUMO, set path via File > Settings |
| `Port 8813 in use` | Matikan proses SUMO lain, restart app |
| `PyQt6 not available` | `pip install PyQt6` / `bash setup.sh` |
| Map tidak muncul di dropdown | Jalankan `scripts/siapkan_map.sh` dulu |

## License

GPL v2
