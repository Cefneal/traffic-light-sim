# TLS — Traffic Light Simulation

Aplikasi desktop simulasi lalu lintas skala kota dengan **SUMO engine** + **Python PyQt6**.

## Fitur

- **3 map preset**: Pamulang, Silicon Valley, Tokyo — masing-masing dgn lampu merah & kendaraan realistis
- **4 algoritma TL**: Fixed-Time, Actuated, Green Wave, Max-Pressure
- **Dashboard real-time**: Grafik kecepatan rata-rata, waktu tunggu, throughput, antrian
- **Import OSM**: Download dari OpenStreetMap → langsung bisa simulate
- **Multi-platform**: Linux, Windows, macOS

## ⚡ Cara Cepat (Pre-built executable)

> **Syarat**: SUMO harus sudah terinstall.

1. Download dari [Releases](https://github.com/Cefneal/traffic-light-sim/releases)
2. Extract & jalankan `tls` (Linux) / `tls.exe` (Windows)

Pre-built executable di-build otomatis via GitHub Actions tiap push ke `main`.

---

## Instalasi SUMO

Aplikasi **membutuhkan SUMO** — engine simulasi lalu lintas.

### Linux (Ubuntu/Debian)
```bash
sudo apt install sumo sumo-tools
```

### Windows
1. Download installer dari [SUMO Downloads](https://sumo.dlr.de/docs/Downloads.php) (pilih versi **1.20.0** atau lebih baru)
2. Jalankan installer — **pastikan centang "Add SUMO to PATH"**
3. Atau: set environment variable `SUMO_HOME` ke folder instalasi SUMO

### macOS
```bash
brew install sumo
```

### Verifikasi
```bash
sumo --version
```
Harus muncul versi SUMO (minimal 1.20.x).

> **Catatan Python**: Aplikasi ini kompatibel dengan Python 3.10–3.13. Python 3.14 **belum didukung penuh** karena beberapa library (PyQt6) belum siap wheels-nya.

---

## Cara 1: Jalankan dari source (Python)

### Setup
```bash
git clone https://github.com/Cefneal/traffic-light-sim.git
cd traffic-light-sim

# Linux / macOS
bash setup.sh

# Windows (CMD)
setup.bat

# Windows (PowerShell — recommended)
.\setup.ps1
```

### Jalankan
```bash
# Linux / macOS
source venv/bin/activate
python -m app.main

# Windows (CMD)
venv\Scripts\activate & python -m app.main

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1 ; python -m app.main
```

---

## Cara 2: Build executable sendiri

### Linux / macOS
```bash
bash setup.sh --build
./dist/tls
```

### Windows
```cmd
pip install pyinstaller
pyinstaller tls.spec --clean -y
dist\tls\tls.exe
```

Atau via GitHub Actions — push tag `v*` ke repo, workflow otomatis build + upload ke Releases.

File executable ada di folder `dist/`.

---

## Cara Pakai

1. Pilih map dari dropdown (Pamulang / Silicon Valley / Tokyo)
2. Atur algoritma TL di panel Configuration
3. Klik **▶ Play** — simulasi berjalan
4. Dashboard real-time di panel kanan
5. Export CSV/JSON via File → Export

### Map Custom
1. Download OSM dari [OpenStreetMap](https://www.openstreetmap.org/export)
2. File → Import OSM → pilih file .osm
3. Atau: `bash scripts/siapkan_map.sh /path/map.osm`

---

## Struktur Proyek

```
app/         Kode utama (engine + GUI + metrics + models)
sim/         Data simulasi (map per folder)
scripts/     Script utilitas
tests/       Unit tests
```

## Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| GUI | PyQt6 |
| Charts | pyqtgraph |
| Engine | SUMO (via TraCI) |
| Database | SQLite |

## Troubleshooting

| Problem | Solusi |
|---------|--------|
| `SUMO not found` | Install SUMO, set `SUMO_HOME` env var, atau set path via File > Settings |
| `PyQt6 not available` | Aktifkan virtual environment dulu: `venv\Scripts\Activate.ps1` atau `source venv/bin/activate` |
| `Port 8813 in use` | Matikan proses SUMO lain, restart app |
| TL tidak muncul di map | Beberapa TL mungkin tidak punya posisi di net.xml — ini normal |
| Map tidak muncul di dropdown | `bash scripts/siapkan_map.sh` dulu |
| Python 3.14 error | Gunakan Python 3.12/3.13 — 3.14 belum kompatibel dengan PyQt6 |

## License

GPL v2
