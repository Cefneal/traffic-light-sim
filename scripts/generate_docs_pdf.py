#!/usr/bin/env python3
"""Generate comprehensive TLS Documentation PDF (Bahasa Indonesia)"""

from pathlib import Path
import weasyprint

OUTPUT = Path(__file__).resolve().parent.parent / "TLS-Dokumentasi.pdf"

HTML = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<style>
@page {
    size: A4;
    margin: 2cm 1.8cm;
    @bottom-center {
        content: counter(page);
        font: 9px Helvetica;
        color: #888;
    }
}
body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 9.5px;
    line-height: 1.55;
    color: #333;
}
h1 {
    font-size: 28px;
    color: #fff;
    background: #2e84c4;
    padding: 12px 20px;
    margin: 0;
}
h2 {
    font-size: 16px;
    color: #2e84c4;
    border-bottom: 2px solid #2e84c4;
    padding-bottom: 4px;
    margin: 22px 0 10px;
}
h3 {
    font-size: 12px;
    color: #2c3e50;
    margin: 16px 0 6px;
}
h4 {
    font-size: 10px;
    color: #555;
    margin: 12px 0 4px;
}
.cover { text-align: center; padding-top: 100px; }
.cover h1 { font-size: 48px; background: none; color: #2e84c4; padding: 0; }
.cover .subtitle { font-size: 16px; color: #666; margin: 8px 0; }
.cover .meta { margin-top: 50px; font-size: 10px; color: #888; }
.cover .meta p { margin: 2px 0; }
table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 8.5px;
}
th {
    background: #2e84c4;
    color: #fff;
    padding: 5px 6px;
    text-align: left;
    font-weight: bold;
}
td {
    padding: 4px 6px;
    border: 1px solid #ddd;
    vertical-align: top;
}
tr:nth-child(even) td { background: #f5f7fa; }
pre {
    background: #282c34;
    color: #e0e0e0;
    padding: 6px 10px;
    border-radius: 4px;
    font: 7.5px/1.4 "Courier New", monospace;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-word;
}
code {
    font: 8px/1.3 "Courier New", monospace;
    background: #f0f0f0;
    padding: 1px 4px;
    border-radius: 2px;
}
ul { padding-left: 18px; }
li { margin: 2px 0; }
.note {
    background: #fef9e7;
    border-left: 3px solid #e67e22;
    padding: 6px 10px;
    margin: 8px 0;
    font-size: 8.5px;
}
.fix-note {
    background: #e8f8f5;
    border-left: 3px solid #2ecc71;
    padding: 6px 10px;
    margin: 8px 0;
    font-size: 8.5px;
}
.warn-note {
    background: #fdedec;
    border-left: 3px solid #e74c3c;
    padding: 6px 10px;
    margin: 8px 0;
    font-size: 8.5px;
}
.page-break { page-break-before: always; }
.small { font-size: 7.5px; color: #999; }
.center { text-align: center; }
.glossary-term { font-weight: bold; color: #2e84c4; }
</style>
</head>
<body>

<!-- ==================== COVER ==================== -->
<div class="cover">
<h1>TLS</h1>
<p class="subtitle">Traffic Light Simulation</p>
<p style="font-size:12px; color:#999;">Dokumentasi Lengkap &amp; Analisis Performa</p>
<div class="meta">
<p>Versi 1.0.0</p>
<p>Engine: SUMO 1.27 + TraCI</p>
<p>GUI: PyQt6 &middot; Chart: pyqtgraph</p>
<p>Bahasa: Python 3.10&ndash;3.13</p>
<p>Platform: Linux / Windows / macOS</p>
</div>
</div>

<!-- ==================== DAFTAR ISI ==================== -->
<div class="page-break"></div>
<h2>Daftar Isi</h2>
<ol>
<li><a href="#s1">Gambaran Umum Proyek</a></li>
<li><a href="#s2">Tech Stack &amp; Istilah Penting</a></li>
<li><a href="#s3">Struktur Folder (Project Tree)</a></li>
<li><a href="#s4">Panduan Memulai (Quick Start)</a></li>
<li><a href="#s5">Tutorial Lengkap Git</a></li>
<li><a href="#s6">Arsitektur Kode (MVC)</a></li>
<li><a href="#s7">Analisis Performa &amp; Bottleneck</a></li>
<li><a href="#s8">Prioritas Perbaikan &amp; Penanggung Jawab</a></li>
<li><a href="#s9">Cara Build &amp; Deploy</a></li>
<li><a href="#s10">Strategi Testing</a></li>
<li><a href="#s11">Glosarium Istilah</a></li>
<li><a href="#s12">Lampiran: Referensi File Penting</a></li>
</ol>

<!-- ==================== 1. GAMBARAN UMUM ==================== -->
<div class="page-break" id="s1"></div>
<h2>1. Gambaran Umum Proyek</h2>

<h3>1.1 Apa Itu TLS?</h3>
<p><strong>TLS (Traffic Light Simulation)</strong> adalah aplikasi desktop untuk simulasi lalu lintas skala kota. Aplikasi ini menggunakan <strong>SUMO</strong> (Simulation of Urban MObility) sebagai engine simulasi, dan menyediakan GUI interaktif real-time untuk mengatur, memantau, dan menganalisis lampu lalu lintas (TL).</p>

<h3>1.2 Fitur Unggulan</h3>
<ul>
<li><strong>3 map preset:</strong> Pamulang (Indonesia), Silicon Valley (USA), Tokyo (Japan) &mdash; masing-masing dengan TL dan kendaraan realistis</li>
<li><strong>4 algoritma TL:</strong> Fixed-Time, Actuated, Green Wave, Max-Pressure &mdash; bisa dipilih dan dibandingkan</li>
<li><strong>Dashboard real-time:</strong> Grafik kecepatan rata-rata, waktu tunggu, throughput, panjang antrian, konsumsi BBM, emisi CO₂</li>
<li><strong>Import OSM:</strong> Download peta dari OpenStreetMap &rarr; langsung bisa disimulasi</li>
<li><strong>Ekspor CSV/JSON:</strong> Data simulasi bisa diekspor untuk analisis lanjutan</li>
<li><strong>Multi-platform:</strong> Linux (Ubuntu), Windows (10/11), macOS</li>
</ul>

<h3>1.3 Latar Belakang &amp; Masalah</h3>
<p>Lampu lalu lintas di banyak kota masih menggunakan pengaturan waktu statis (fixed-time). Hal ini menyebabkan:</p>
<ul>
<li>Kemacetan di jam sibuk karena TL tidak bisa menyesuaikan dengan volume kendaraan</li>
<li>Pemborosan bahan bakar &amp; polusi dari kendaraan yang berhenti terlalu lama</li>
<li>Waktu tempuh yang tidak stabil</li>
</ul>
<p>TLS memungkinkan peneliti dan perencana kota untuk menguji algoritma TL adaptif (Actuated, Max-Pressure, Green Wave) pada skenario lalu lintas nyata atau sintetis sebelum diimplementasikan di lapangan.</p>

<h3>1.4 Siapa Saja yang Terlibat?</h3>
<table>
<tr><th>Peran</th><th>Tanggung Jawab</th><th>Bagian Kode</th></tr>
<tr>
    <td><strong>Backend Engineer</strong></td>
    <td>TraCI client, koneksi SUMO, caching, subscription, thread safety</td>
    <td><code>traci_client.py</code>, <code>sim_controller.py</code> (bagian TraCI)</td>
</tr>
<tr>
    <td><strong>Algorithm Engineer</strong></td>
    <td>Fixed-Time, Actuated, Max-Pressure, Green Wave logic</td>
    <td><code>tl_algorithms.py</code>, <code>traffic_light.py</code></td>
</tr>
<tr>
    <td><strong>Frontend / GUI Engineer</strong></td>
    <td>Map rendering, dashboard, kontrol panel, user experience</td>
    <td><code>map_viewer.py</code>, <code>dashboard.py</code>, <code>main_window.py</code></td>
</tr>
<tr>
    <td><strong>DevOps / Build Engineer</strong></td>
    <td>PyInstaller build, GitHub Actions CI/CD, release management</td>
    <td><code>tls.spec</code>, <code>.github/workflows/build.yml</code></td>
</tr>
<tr>
    <td><strong>QA / Tester</strong></td>
    <td>Unit test, integration test, performance benchmark, regression</td>
    <td><code>tests/</code> (akan dibuat)</td>
</tr>
</table>

<!-- ==================== 2. TECH STACK ==================== -->
<div class="page-break" id="s2"></div>
<h2>2. Tech Stack &amp; Istilah Penting</h2>

<h3>2.1 Teknologi yang Digunakan</h3>
<table>
<tr><th>Komponen</th><th>Teknologi</th><th>Versi</th><th>Fungsi</th></tr>
<tr><td>Simulation Engine</td><td>SUMO</td><td>1.20+ (1.27)</td><td>Menjalankan simulasi lalu lintas (kendaraan, jalan, TL)</td></tr>
<tr><td>Komunikasi</td><td>TraCI</td><td>bawaan SUMO</td><td>Protokol TCP untuk kontrol real-time dari Python ke SUMO</td></tr>
<tr><td>GUI Desktop</td><td>PyQt6</td><td>&gt;= 6.5</td><td>Window, map, kontrol, menu &mdash; semua tampilan aplikasi</td></tr>
<tr><td>Grafik Real-time</td><td>pyqtgraph</td><td>&gt;= 0.13</td><td>Chart kecepatan, throughput, dll di dashboard</td></tr>
<tr><td>PDF (opsional)</td><td>weasyprint</td><td>&gt;= 60</td><td>Export laporan ke PDF</td></tr>
<tr><td>Bahasa</td><td>Python</td><td>3.10&ndash;3.13</td><td>Semua kode aplikasi</td></tr>
<tr><td>Database</td><td>SQLite</td><td>bawaan Python</td><td>Menyimpan hasil simulasi &amp; skenario</td></tr>
</table>

<h3>2.2 Glosarium Istilah Penting</h3>
<table>
<tr><th>Istilah</th><th>Kepanjangan</th><th>Penjelasan</th></tr>
<tr>
    <td><span class="glossary-term">SUMO</span></td>
    <td>Simulation of Urban MObility</td>
    <td>Engine simulasi lalu lintas open-source dari DLR (Jerman). Bisa simulasi seluruh kota dengan ribuan kendaraan.</td>
</tr>
<tr>
    <td><span class="glossary-term">TraCI</span></td>
    <td>Traffic Control Interface</td>
    <td>Protokol TCP yang menghubungkan Python ke SUMO. Semua perintah (get posisi kendaraan, set fase TL, dll) lewat TraCI.</td>
</tr>
<tr>
    <td><span class="glossary-term">TL</span></td>
    <td>Traffic Light</td>
    <td>Lampu lalu lintas. Di TLS, setiap TL punya beberapa fase (hijau, kuning, merah) dengan durasi tertentu.</td>
</tr>
<tr>
    <td><span class="glossary-term">Fase TL</span></td>
    <td>TL Phase</td>
    <td>Kondisi lampu pada suatu waktu, misal: "ggggrrrr" = 4 lajur hijau + 4 lajur merah.</td>
</tr>
<tr>
    <td><span class="glossary-term">Fixed-Time</span></td>
    <td>&mdash;</td>
    <td>Algoritma TL paling sederhana: setiap fase punya durasi tetap, berputar terus.</td>
</tr>
<tr>
    <td><span class="glossary-term">Actuated</span></td>
    <td>&mdash;</td>
    <td>Algoritma yang memperpanjang fase hijau jika ada kendaraan mendekat (via detector/induction loop).</td>
</tr>
<tr>
    <td><span class="glossary-term">Max-Pressure</span></td>
    <td>&mdash;</td>
    <td>Algoritma yang memilih fase TL berdasarkan jumlah kendaraan di ruas jalan terpadat. Paling kompleks &amp; adaptif.</td>
</tr>
<tr>
    <td><span class="glossary-term">Green Wave</span></td>
    <td>&mdash;</td>
    <td>Algoritma yang menyelaraskan TL secara berurutan agar kendaraan bisa melewati banyak TL tanpa berhenti.</td>
</tr>
<tr>
    <td><span class="glossary-term">Subscription</span></td>
    <td>&mdash;</td>
    <td>Fitur TraCI: kita bilang ke SUMO "tolong kirim data X setiap step" sekali, lalu tinggal baca hasilnya. Lebih cepat daripada manggil perintah setiap step.</td>
</tr>
<tr>
    <td><span class="glossary-term">Step / Simulation Step</span></td>
    <td>&mdash;</td>
    <td>Satu iterasi simulasi (default 1 detik). SUMO menghitung posisi kendaraan baru, TL berpindah fase, dll.</td>
</tr>
<tr>
    <td><span class="glossary-term">Thread / Threading</span></td>
    <td>&mdash;</td>
    <td>Eksekusi paralel. Simulasi jalan di thread sendiri, GUI di thread utama. Kalau akses data barengan tanpa pengaman &rarr; crash (race condition).</td>
</tr>
<tr>
    <td><span class="glossary-term">Race Condition</span></td>
    <td>&mdash;</td>
    <td>Dua thread mengakses data yang sama pada saat bersamaan, menyebabkan hasil tidak terduga / crash.</td>
</tr>
<tr>
    <td><span class="glossary-term">PyInstaller</span></td>
    <td>&mdash;</td>
    <td>Tools untuk mengemas aplikasi Python jadi executable (.exe di Windows, binary di Linux).</td>
</tr>
<tr>
    <td><span class="glossary-term">GitHub Actions</span></td>
    <td>&mdash;</td>
    <td>Layanan CI/CD dari GitHub: otomatis menjalankan build &amp; test saat kita push kode.</td>
</tr>
</table>

<h3>2.3 Kenapa Python 3.14 Tidak Didukung?</h3>
<p>Python 3.14 masih terlalu baru. Library <strong>PyQt6</strong> dan <strong>pyqtgraph</strong> belum merilis wheel (pre-built binary) untuk Python 3.14. Akibatnya, pip akan mencoba kompilasi dari source code, yang biasanya gagal di Windows dan memakan waktu lama di Linux. Gunakan Python 3.12 atau 3.13.</p>

<!-- ==================== 3. STRUKTUR FOLDER ==================== -->
<div class="page-break" id="s3"></div>
<h2>3. Struktur Folder (Project Tree)</h2>
<p>Proyek ini mengikuti pola <strong>MVC</strong> (Model-View-Controller) &mdash; dijelaskan lebih lanjut di Bab 6.</p>

<pre>traffic-light-sim/
|-- app/                              # KODE UTAMA APLIKASI
|   |-- main.py                       # Entry point: dijalankan dengan "python -m app.main"
|   |
|   |-- engine/                       # LAYER MODEL + CONTROLLER
|   |   |-- traci_client.py           # TraCI wrapper (Model) - 499 baris
|   |   |-- sim_controller.py         # Loop simulasi (Controller) - 298 baris
|   |   |-- tl_algorithms.py          # 4 algoritma TL - 173 baris
|   |   |-- osm_importer.py           # Import OSM -&gt; netconvert - ~80 baris
|   |
|   |-- gui/                          # LAYER VIEW (tampilan)
|   |   |-- map_viewer.py             # Map + kendaraan + TL (QGraphicsView) - 674 baris
|   |   |-- main_window.py            # Layout jendela, menu, signal - 233 baris
|   |   |-- dashboard.py              # Chart real-time (pyqtgraph) - 181 baris
|   |   |-- controls.py               # Toolbar Play/Pause/Speed - ~150 baris
|   |   |-- config_panel.py           # Panel konfigurasi algoritma
|   |   |-- settings_dialog.py        # Dialog pengaturan aplikasi
|   |   |-- scenario_dialog.py        # Dialog simpan/load skenario
|   |   |-- tile_provider.py          # Background peta dari OSM tiles
|   |
|   |-- models/                       # DATA CLASSES
|   |   |-- traffic_light.py          # TLPhase, TrafficLight
|   |   |-- vehicle.py                # Vehicle (posisi, kecepatan, sudut)
|   |
|   |-- metrics/                      # PENGUMPUL DATA
|   |   |-- collector.py              # MetricsCollector (ring buffer)
|   |   |-- storage.py                # Simpan ke SQLite / JSON
|   |
|   |-- utils/                        # UTILITAS
|       |-- config.py                 # Baca/tulis konfigurasi (JSON)
|       |-- localization.py           # Bahasa Indonesia / Inggris
|       |-- logger.py                 # Logging (loguru)
|
|-- sim/                              # DATA SIMULASI (map per folder)
|   |-- pamulang/                     # Map Pamulang, Indonesia
|   |-- silicon_valley/               # Map Silicon Valley, USA
|   |-- tokyo/                        # Map Tokyo, Japan
|
|-- scripts/                          # SCRIPT UTILITAS
|   |-- setup_maps.py                 # Inisialisasi folder map
|   |-- generate_logo.py              # Generate icon.png + icon.ico
|   |-- generate_docs_pdf.py          # PEMBUAT PDF INI
|   |-- add_tls_to_network.py         # Tambah TL ke jaringan
|
|-- tests/                            # (AKAN DIBUAT - lihat Bab 10)
|
|-- .github/workflows/
|   |-- build.yml                     # CI/CD pipeline (GitHub Actions)
|
|-- setup.bat                         # Setup untuk Windows (CMD)
|-- setup.ps1                         # Setup untuk Windows (PowerShell)
|-- setup.sh                          # Setup untuk Linux / macOS
|-- tls.spec                          # Konfigurasi PyInstaller
|-- requirements.txt                  # Daftar dependency Python
|-- README.md                         # Dokumentasi cepat
|-- TLS-Dokumentasi.pdf               # DOKUMEN INI</pre>

<!-- ==================== 4. QUICK START ==================== -->
<div class="page-break" id="s4"></div>
<h2>4. Panduan Memulai (Quick Start)</h2>

<h3>4.1 Prasyarat</h3>
<ol>
<li><strong>Python 3.10, 3.11, 3.12, atau 3.13</strong> &mdash; Install dari <a href="https://www.python.org/downloads/">python.org</a>. Centang "Add Python to PATH" saat instalasi.</li>
<li><strong>SUMO 1.20 atau lebih baru</strong> &mdash; Download dari <a href="https://sumo.dlr.de/docs/Downloads.php">sumo.dlr.de</a>. Pastikan folder <code>bin/</code> terdaftar di PATH environment variable, atau set <code>SUMO_HOME</code> ke folder instalasi.</li>
</ol>

<div class="warn-note"><strong>PERINGATAN:</strong> Python 3.14 TIDAK didukung. PyQt6 dan pyqtgraph belum punya wheel untuk 3.14.</div>

<h3>4.2 Cara Clone &amp; Setup</h3>

<h4>Linux / macOS</h4>
<pre>git clone https://github.com/Cefneal/traffic-light-sim.git
cd traffic-light-sim
bash setup.sh
source venv/bin/activate
python -m app.main</pre>

<h4>Windows (PowerShell &mdash; disarankan)</h4>
<pre>git clone https://github.com/Cefneal/traffic-light-sim.git
cd traffic-light-sim
.\setup.ps1
.\venv\Scripts\Activate.ps1 ; python -m app.main</pre>

<h4>Windows (CMD)</h4>
<pre>git clone https://github.com/Cefneal/traffic-light-sim.git
cd traffic-light-sim
setup.bat
venv\Scripts\activate & python -m app.main</pre>

<h3>4.3 Penjelasan Langkah-langkah</h3>
<ol>
<li><strong>git clone</strong> &mdash; Mendownload semua kode dari GitHub ke komputer lokal</li>
<li><strong>cd</strong> &mdash; Masuk ke folder proyek</li>
<li><strong>setup.bat / setup.ps1 / setup.sh</strong> &mdash; Script yang otomatis: bikin virtual environment (venv), install semua dependency Python (PyQt6, pyqtgraph, traci, weasyprint)</li>
<li><strong>Activate venv</strong> &mdash; Mengaktifkan lingkungan Python terisolasi (biar library yang diinstall gak bentrok dengan Python sistem)</li>
<li><strong>python -m app.main</strong> &mdash; Menjalankan aplikasi</li>
</ol>

<h3>4.4 Cara Pakai Aplikasi</h3>
<ol>
<li>Pilih map dari dropdown (Pamulang / Silicon Valley / Tokyo)</li>
<li>Atur algoritma TL di panel Configuration (Fixed-Time / Actuated / Green Wave / Max-Pressure)</li>
<li>Klik tombol <strong>Play</strong> (&blacktriangleright;) &mdash; simulasi berjalan</li>
<li>Lihat grafik real-time di panel Dashboard (kanan)</li>
<li>Atur kecepatan simulasi dengan slider Speed</li>
<li>Export data via File &rarr; Export CSV atau Export JSON</li>
</ol>

<!-- ==================== 5. TUTORIAL GIT ==================== -->
<div class="page-break" id="s5"></div>
<h2>5. Tutorial Lengkap Git</h2>

<h3>5.1 Apa Itu Git?</h3>
<p><strong>Git</strong> adalah sistem version control. Git mencatat setiap perubahan kode &mdash; siapa yang mengubah, kapan, dan apa yang diubah. Ini penting untuk:</p>
<ul>
<li>Kerja tim &mdash; beberapa orang bisa mengedit kode yang sama tanpa konflik</li>
<li>Riwayat &mdash; bisa lihat/bandingkan versi kode sebelumnya</li>
<li>Rollback &mdash; kalau ada error, bisa kembali ke versi yang stabil</li>
<li>Branching &mdash; mengembangkan fitur baru tanpa mengganggu kode utama</li>
</ul>

<h3>5.2 Install Git</h3>
<table>
<tr><th>OS</th><th>Perintah</th></tr>
<tr><td>Linux (Ubuntu/Debian)</td><td><code>sudo apt install git</code></td></tr>
<tr><td>macOS</td><td><code>brew install git</code></td></tr>
<tr><td>Windows</td><td>Download dari <a href="https://git-scm.com/">git-scm.com</a> &mdash; pastikan centang "Git Bash" dan "Add to PATH"</td></tr>
</table>

<h3>5.3 Konfigurasi Awal (Hanya Sekali)</h3>
<pre>git config --global user.name "Nama Kamu"
git config --global user.email "email@example.com"
git config --global init.defaultBranch main</pre>

<h3>5.4 Clone Repository (Download Pertama Kali)</h3>
<pre>git clone https://github.com/Cefneal/traffic-light-sim.git
cd traffic-light-sim</pre>
<p>Penjelasan:</p>
<ul>
<li><code>git clone</code> &mdash; Download seluruh riwayat proyek dari GitHub ke folder lokal</li>
<li>Setelah clone, folder <code>traffic-light-sim/</code> akan muncul dengan semua file</li>
<li>Git otomatis membuat remote bernama <code>origin</code> yang mengarah ke GitHub</li>
</ul>

<h3>5.5 Status &amp; Log (Cek Kondisi)</h3>
<pre># Cek file yang berubah
git status

# Lihat riwayat commit
git log --oneline --graph --all

# Bandingkan perubahan yang belum di-commit
git diff

# Lihat detail commit terakhir
git show</pre>

<h3>5.6 Pull (Ambil Perubahan Terbaru)</h3>
<pre>git pull origin main</pre>
<p>Sebelum mulai bekerja, selalu <code>git pull</code> dulu untuk mendapatkan perubahan terbaru dari GitHub.</p>

<h3>5.7 Branch (Cabang)</h3>
<p><strong>Branch</strong> memungkinkan kita mengembangkan fitur secara terpisah tanpa mengganggu kode utama (<code>main</code>).</p>
<pre># Lihat daftar branch
git branch -a

# Buat branch baru
git checkout -b feature/perbaikan-kinerja

# Pindah ke branch lain
git checkout main

# Hapus branch (sudah di-merge)
git branch -d feature/perbaikan-kinerja</pre>
<p>Diagram alur branch:</p>
<pre>main:     A --- B --- C --- D --- E
                 \         /
feature:          X --- Y</pre>
<p>Keterangan: <code>feature</code> bercabang dari commit B, membuat commit X dan Y, lalu di-merge kembali ke main di commit D.</p>

<h3>5.8 Add, Commit, Push (Siklus Harian)</h3>
<p><strong>Setiap kali selesai mengerjakan bagian kecil, commit.</strong></p>
<pre># 1. Cek apa saja yang berubah
git status

# 2. Stage file yang ingin di-commit
git add app/engine/sim_controller.py
git add app/engine/traci_client.py

# Atau stage semua file sekaligus (hati-hati)
git add -A

# 3. Commit dengan pesan yang jelas
git commit -m "fix: kurangi TraCI calls di simulation loop"

# 4. Push ke GitHub
git push origin nama-branch-kamu</pre>

<h3>5.9 Contoh Skenario Lengkap</h3>
<pre># Pagi hari: pull dulu
git checkout main
git pull origin main

# Buat branch untuk fitur baru
git checkout -b fix/fuel-loop

# Edit file traci_client.py
# ... (perbaiki kode) ...

git add app/engine/traci_client.py
git commit -m "fix: ganti fuel loop dengan subscription"

# Push ke GitHub
git push -u origin fix/fuel-loop

# Di GitHub: buat Pull Request (PR)
# Minta review dari tim
# Setelah disetujui: merge ke main

# Hapus branch lokal
git checkout main
git pull origin main
git branch -d fix/fuel-loop</pre>

<h3>5.10 Pull Request (PR)</h3>
<p><strong>Pull Request</strong> adalah permintaan untuk menggabungkan kode dari branch kamu ke branch utama. Langkah-langkah:</p>
<ol>
<li>Push branch kamu ke GitHub (lihat 5.9)</li>
<li>Buka repo di GitHub.com &rarr; klik "Compare &amp; pull request"</li>
<li>Tulis judul dan deskripsi perubahan</li>
<li>Klik "Create pull request"</li>
<li>Tim akan review, memberi komentar, atau menyetujui</li>
<li>Setelah disetujui, klik "Merge pull request"</li>
</ol>

<h3>5.11 Aturan Penulisan Commit</h3>
<table>
<tr><th>Prefix</th><th>Arti</th><th>Contoh</th></tr>
<tr><td><code>fix:</code></td><td>Perbaikan bug</td><td><code>fix: race condition di thread TraCI</code></td></tr>
<tr><td><code>feat:</code></td><td>Fitur baru</td><td><code>feat: tambah dialog import OSM</code></td></tr>
<tr><td><code>perf:</code></td><td>Optimasi kinerja</td><td><code>perf: cache hasil subscription kendaraan</code></td></tr>
<tr><td><code>docs:</code></td><td>Perubahan dokumentasi</td><td><code>docs: update README setup Windows</code></td></tr>
<tr><td><code>refactor:</code></td><td>Perubahan kode (tanpa ubah fitur)</td><td><code>refactor: pisahkan logika TL building</code></td></tr>
<tr><td><code>chore:</code></td><td>Maintenance</td><td><code>chore: update requirements.txt</code></td></tr>
</table>

<h3>5.12 Tag &amp; Release</h3>
<p><strong>Tag</strong> menandai versi tertentu di riwayat Git. Tag memicu build otomatis di GitHub Actions.</p>
<pre># Buat tag
git tag -a v1.0.0 -m "Release v1.0.0"

# Push tag ke GitHub
git push origin v1.0.0

# Lihat daftar tag
git tag -l

# Hapus tag (jika salah)
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0</pre>
<p>Setelah tag di-push, GitHub Actions akan:</p>
<ol>
<li>Menjalankan semua test</li>
<li>Build executable Linux + Windows</li>
<li>Upload ke halaman Releases</li>
</ol>

<h3>5.13 Mengatasi Konflik Merge</h3>
<p>Konflik terjadi ketika dua orang mengubah baris yang sama di file yang sama. Git tidak tahu mana yang benar &rarr; kita harus memilih secara manual.</p>
<pre># Saat merge, Git akan bilang: "CONFLICT in file.txt"
# Buka file tersebut. Cari tanda ini:
# &lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD
# kode dari branch main
# =======
# kode dari branch kamu
# &gt;&gt;&gt;&gt;&gt;&gt;&gt; nama-branch

# Hapus tanda &lt;&lt;&lt; === &gt;&gt;&gt;, sisakan kode yang benar
# Lalu:
git add file.txt
git commit -m "merge: resolve conflict di file.txt"</pre>

<h3>5.14 Git Stash (Simpan Sementara)</h3>
<p>Kalau lagi ngerjain sesuatu tapi butuh pindah branch dulu:</p>
<pre># Simpan perubahan sementara
git stash

# Pindah branch, pull, dll
git checkout main
git pull

# Kembali kerja
git checkout feature/*
git stash pop</pre>

<h3>5.15 Git Rebase (Alternatif Merge yang Lebih Rapi)</h3>
<p><code>rebase</code> mengambil commit dari branch kita dan menempelkannya di ujung branch main. Hasilnya riwayat lebih linear &amp; bersih.</p>
<pre>git checkout feature/*
git rebase main
# Jika ada konflik, selesaikan, lalu:
git rebase --continue
# Kalau bingung / mau batal:
git rebase --abort</pre>

<div class="note"><strong>Catatan:</strong> Jangan <code>rebase</code> di branch yang sudah dipush dan digunakan orang lain. Rebase hanya untuk branch lokal.</div>

<!-- ==================== 6. ARSITEKTUR ==================== -->
<div class="page-break" id="s6"></div>
<h2>6. Arsitektur Kode (MVC)</h2>

<h3>6.1 Pola MVC (Model-View-Controller)</h3>
<p>TLS menggunakan pola arsitektur <strong>MVC</strong> &mdash; memisahkan data (Model), logika (Controller), dan tampilan (View):</p>
<ul>
<li><strong>Model</strong> (<code>TraCIClient</code>) &mdash; Bertanggung jawab atas semua komunikasi dengan SUMO via TraCI. Menyediakan data mentah (posisi kendaraan, status TL, dll).</li>
<li><strong>Controller</strong> (<code>SimController</code>) &mdash; Mengatur alur simulasi. Setiap step: majukan SUMO, jalankan algoritma TL, kumpulkan metrik, kirim data ke View.</li>
<li><strong>View</strong> (<code>MapViewer</code>, <code>DashboardPanel</code>, dll) &mdash; Menampilkan data ke pengguna. Tidak boleh langsung bertanya ke SUMO &mdash; harus lewat Controller.</li>
</ul>

<pre>  +------------------+    Signal PyQt6     +------------------+
  |  SimController   | -------------------&gt; |  MapViewer       |
  |  (Controller)    |     (setiap step)     |  DashboardPanel  |
  |  thread terpisah |                       |  ControlsToolbar |
  +--------+---------+                       +------------------+
           |
     punya |  (model)
           v
  +------------------+    TCP loopback
  |  TraCIClient     | &lt;====&gt; SUMO (TraCI)
  |  (Model)         |       port 8813
  +------------------+</pre>

<h3>6.2 Aliran Data Setiap Step</h3>
<p>Simulasi berjalan di thread terpisah (~30 step/detik). GUI membaca data dari subscription (tanpa panggilan TraCI tambahan).</p>
<table>
<tr><th>Urutan</th><th>Thread</th><th>Aksi</th><th>Panggilan TraCI</th></tr>
<tr><td>1</td><td>Sim</td><td>get_vehicle_ids() &rarr; subscribe vehicle baru</td><td>2</td></tr>
<tr><td>2</td><td>Sim</td><td>simulationStep() &rarr; SUMO maju 1 step</td><td>1</td></tr>
<tr><td>3</td><td>Sim</td><td>Baca data kendaraan dari subscription (cached)</td><td>0</td></tr>
<tr><td>4</td><td>Sim</td><td><strong>[BOTTLENECK]</strong> Hitung total fuel/CO2 &rarr; loop semua kendaraan</td><td>N &times; 2</td></tr>
<tr><td>5</td><td>Sim</td><td>Jalankan algoritma TL &rarr; baca data edge, set phase</td><td>10&ndash;1500</td></tr>
<tr><td>6</td><td>Sim</td><td>Kirim signal 'step' ke GUI (via PyQt6)</td><td>0</td></tr>
<tr><td>7</td><td>GUI</td><td>Baca posisi kendaraan dari subscription (cached)</td><td>0</td></tr>
<tr><td>8</td><td>GUI</td><td>Update TL state dari subscription</td><td>0</td></tr>
</table>

<h3>6.3 TraCIClient (Model)</h3>
<p>File: <code>app/engine/traci_client.py</code> (499 baris).</p>
<p><strong>Fungsi utama:</strong></p>
<ul>
<li><strong>connect()</strong> &mdash; Membuka koneksi TCP ke SUMO di port 8813</li>
<li><strong>simulation_step()</strong> &mdash; Menyuruh SUMO maju satu step</li>
<li><strong>subscribe_*()</strong> &mdash; Berlangganan data (edge, vehicle, TL) agar bisa dibaca tanpa panggilan TraCI tambahan</li>
<li><strong>get_*_cached()</strong> &mdash; Membaca data dari hasil subscription (cepat, 0 panggilan TraCI)</li>
<li><strong>set_tl_phase()</strong> &mdash; Mengubah fase lampu lalu lintas di SUMO</li>
</ul>

<p><strong>Masalah yang diketahui (lihat Bab 7):</strong></p>
<ul>
<li><strong>Thread-unsafe:</strong> Semua method akses <code>traci.*</code> langsung tanpa lock &rarr; crash kalau GUI dan Sim akses barengan</li>
<li><strong>Fuel/CO2 loop:</strong> <code>get_total_fuel_consumption()</code> memanggil <code>getFuelConsumption()</code> per kendaraan &rarr; ribuan panggilan TraCI per step</li>
<li><strong>Subscription leak:</strong> Vehicle di-subscribe tapi tidak pernah di-unsubscribe</li>
</ul>

<h3>6.4 SimController (Controller)</h3>
<p>File: <code>app/engine/sim_controller.py</code> (298 baris).</p>
<p><strong>Fungsi utama:</strong></p>
<ul>
<li><strong>start()</strong> &mdash; Menjalankan SUMO sebagai proses terpisah, konek via TraCI, mulai thread simulasi</li>
<li><strong>_run_loop()</strong> &mdash; Loop utama: subscribe vehicle &rarr; simulationStep() &rarr; baca data &rarr; jalankan algoritma TL &rarr; kumpulkan metrik &rarr; emit signal</li>
<li><strong>pause() / resume() / stop()</strong> &mdash; Kontrol simulasi</li>
<li><strong>set_algorithm()</strong> &mdash; Ganti algoritma TL (Fixed / Actuated / Max-Pressure / Green Wave)</li>
</ul>

<h3>6.5 GUI (View)</h3>
<p>Tiga widget utama:</p>
<ul>
<li><strong>MapViewer</strong> (674 baris): QGraphicsView dengan QTimer ~30 FPS. Menggambar jalan, kendaraan, TL, jejak kendaraan, heatmap, tile OSM.</li>
<li><strong>DashboardPanel</strong> (181 baris): Chart rolling time-series (kecepatan, waktu tunggu, throughput, antrian, BBM, CO2).</li>
<li><strong>ControlsToolbar</strong> (~150 baris): Tombol Play/Pause/Stop, slider Speed, dropdown scenario.</li>
</ul>

<!-- ==================== 7. ANALISIS PERFORMA ==================== -->
<div class="page-break" id="s7"></div>
<h2>7. Analisis Performa &amp; Bottleneck</h2>

<h3>7.1 Ringkasan</h3>
<p>Aplikasi saat ini mengalami <strong>lag parah</strong> karena terlalu banyak panggilan TraCI (protokol TCP). Setiap panggilan TraCI memakan waktu ~100 mikrodetik. Dengan <strong>14.000+ panggilan per step</strong> dan target 30 FPS (30 step/detik), aplikasi menghabiskan sebagian besar waktu menunggu jawaban dari SUMO, bukan menghitung.</p>

<table>
<tr><th>Metrik</th><th>Saat Ini</th><th>Target Setelah Fix</th></tr>
<tr><td>Panggilan TraCI per step</td><td>~14.000+</td><td>~50&ndash;200</td></tr>
<tr><td>FPS GUI (1000 kendaraan)</td><td>8&ndash;12 (adaptive, turun)</td><td>30 (stabil)</td></tr>
<tr><td>Thread safety</td><td>Rawan crash (race condition)</td><td>Aman (shared buffer + lock)</td></tr>
<tr><td>Memory (simulasi 1 jam)</td><td>Terus bertambah (sub leak)</td><td>Stabil</td></tr>
<tr><td>Akurasi timing real-time</td><td>Melenceng (sleep tanpa koreksi)</td><td>&lt; 1% error</td></tr>
</table>

<h3>7.2 P1 &mdash; Critical (Harus Diperbaiki Segera)</h3>
<p>Tiga masalah ini menyebabkan lag paling parah dan crash. <strong>Prioritas tertinggi.</strong></p>

<table>
<tr><th>#</th><th>Masalah</th><th>File:Baris</th><th>Dampak</th><th>Panggilan/Step</th></tr>
<tr>
    <td><strong>1.1</strong></td>
    <td>Loop Fuel/CO<sub>2</sub> per kendaraan</td>
    <td>traci_client.py:401&ndash;423</td>
    <td>Setiap step, looping semua kendaraan (5000+) untuk baca fuel &amp; CO2 masing-masing</td>
    <td>~10.000</td>
</tr>
<tr>
    <td><strong>1.2</strong></td>
    <td>MaxPressure panggil edge berulang</td>
    <td>tl_algorithms.py:84&ndash;116</td>
    <td>Setiap TL, setiap fase, looping semua edge &rarr; panggil getLastStepVehicleNumber() + getLastStepMeanSpeed()</td>
    <td>~1.500</td>
</tr>
<tr>
    <td><strong>1.3</strong></td>
    <td>Race condition thread (GUI + Sim)</td>
    <td>sim_controller.py + map_viewer.py</td>
    <td>Dua thread akses TraCI bersamaan &rarr; crash "setPhase failed: Connection already closed"</td>
    <td>N/A (crash)</td>
</tr>
</table>

<h4>Detail P1.1 &mdash; Fuel/CO₂ Loop</h4>
<pre># traci_client.py:401-423
def get_total_fuel_consumption(self) -> float:
    total = 0.0
    for vid in traci.vehicle.getIDList():       # 5000 ID
        total += traci.vehicle.getFuelConsumption(vid)  # 5000 panggilan TraCI
    return total

# Dipanggil SETIAP STEP di sim_controller.py:208-209
total_fuel = self.traci.get_total_fuel_consumption()  # 5000 panggilan
total_co2 = self.traci.get_total_co2_emission()       # 5000 panggilan</pre>
<div class="fix-note"><strong>FIX:</strong> Tambahkan VAR_FUELCONSUMPTION dan VAR_CO2EMISSION ke daftar subscription kendaraan. Dengan cara ini, data fuel &amp; CO2 otomatis tersedia setelah setiap step tanpa panggilan TraCI tambahan. Alternatif: hitung fuel/CO2 hanya setiap 10 step (karena perubahannya lambat). <strong>Effort: ~4 jam. Penanggung jawab: Backend Engineer.</strong></div>

<h4>Detail P1.2 &mdash; MaxPressure Panggil Edge Berulang</h4>
<pre># tl_algorithms.py:96-108
edge_ids = traci_module.edge.getIDList()[:50]   # 1 panggilan
for i, phase in enumerate(tl.phases):            # ~3 fase
    for eid in edge_ids:                         # ~50 edge
        count = traci_module.edge.getLastStepVehicleNumber(eid)  # 1 panggilan
        speed = traci_module.edge.getLastStepMeanSpeed(eid)      # 1 panggilan
    # Total per TL: 1 + 3 x 50 x 2 = 301 panggilan</pre>
<p>Dengan ~10 TL, MaxPressure saja menghabiskan ~3.000 panggilan/step.</p>
<div class="fix-note"><strong>FIX:</strong> Gunakan metode <code>get_edge_data_cached(eid)</code> yang sudah ada &mdash; ia membaca data dari subscription alih-alih membuat panggilan TraCI baru. Data edge sudah di-subscribe di sim_controller.py:164-165. <strong>Effort: ~3 jam. Penanggung jawab: Algorithm Engineer.</strong></div>

<h4>Detail P1.3 &mdash; Race Condition Thread</h4>
<pre># THREAD 1 (Sim): sim_controller.py:195
self.traci.simulation_step()   # TraCI: perintah SimulationStep (sibuk)

# THREAD 2 (GUI): map_viewer.py:406 (dijalankan ~30 Hz)
vehicles = tc.get_all_vehicles_cached()  # TraCI: getIDList (samaan!)

# Hasilnya:
#   "setPhase failed: Connection already closed"
#   GUI freeze / crash acak</pre>
<div class="fix-note"><strong>FIX:</strong> Implementasi <strong>shared buffer</strong> yang aman untuk thread. Sim thread menulis data kendaraan &amp; TL ke buffer yang dilindungi <code>threading.Lock</code>. GUI thread membaca dari buffer ini. <strong>DILARANG keras memanggil traci.* dari GUI thread.</strong> <strong>Effort: ~8 jam. Penanggung jawab: Backend Engineer + GUI Engineer (kolaborasi).</strong></div>

<h3>7.3 P2 &mdash; High (Harus Diperbaiki)</h3>
<table>
<tr><th>#</th><th>Masalah</th><th>File:Baris</th><th>Dampak</th><th>Panggilan/Step</th></tr>
<tr><td><strong>2.1</strong></td><td>Subscription kendaraan bocor</td><td>sim_controller.py:189&ndash;192</td><td>SUMO makin lambat seiring waktu karena ribuan subscription menumpuk</td><td>N/A</td></tr>
<tr><td><strong>2.2</strong></td><td>Panggil getIDList() 2x redundant</td><td>sim_controller + traci_client</td><td>getIDList() dipanggil dua kali per step</td><td>~2</td></tr>
<tr><td><strong>2.3</strong></td><td>Timing sleep tidak akurat</td><td>sim_controller.py:245&ndash;246</td><td>Simulasi makin lambat vs real-time seiring waktu</td><td>0</td></tr>
<tr><td><strong>2.4</strong></td><td>step_single() kurang parameter step_length</td><td>sim_controller.py:259</td><td>Algoritma actuated tidak berfungsi di single-step mode</td><td>0</td></tr>
</table>

<div class="fix-note"><strong>FIX 2.1:</strong> Setelah setiap step, hitung selisih: kendaraan yang sudah keluar = subscribed - current_ids. Unsubscribe kendaraan yang sudah pergi via <code>traci.vehicle.unsubscribe(vid)</code>. <strong>Effort: ~3 jam. Backend Engineer.</strong></div>

<div class="fix-note"><strong>FIX 2.2:</strong> Cache vehicle IDs dari hasil subscription &mdash; jangan panggil getIDList() dua kali. <strong>Effort: ~1 jam. Backend Engineer.</strong></div>

<div class="fix-note"><strong>FIX 2.3:</strong> Ganti <code>time.sleep(sleep_time)</code> dengan <code>actual_sleep = max(0, target_interval - elapsed_body_time)</code>. <strong>Effort: ~2 jam. Backend Engineer.</strong></div>

<div class="fix-note"><strong>FIX 2.4:</strong> Tambahkan parameter <code>step_length</code> ke pemanggilan <code>self._algorithm_fn(tl, traci, self.current_time, step_length)</code>. <strong>Effort: ~1 jam. Backend Engineer.</strong></div>

<h3>7.4 P3 &mdash; Medium (Perbaikan Tambahan)</h3>
<table>
<tr><th>#</th><th>Masalah</th><th>File:Baris</th><th>Dampak</th></tr>
<tr><td><strong>3.1</strong></td><td>TL get_tl_ids() dipanggil 2x per frame GUI</td><td>map_viewer.py:526,543</td><td>Panggilan TraCI ganda per update</td></tr>
<tr><td><strong>3.2</strong></td><td>Dashboard update 30 Hz (boros CPU)</td><td>main_window.py:114&ndash;128</td><td>Chart re-render 30/detik padahal tidak perlu</td></tr>
<tr><td><strong>3.3</strong></td><td>Cleanup kendaraan O(n) scan semua dict</td><td>map_viewer.py:508&ndash;519</td><td>Iterasi semua item setiap frame</td></tr>
<tr><td><strong>3.4</strong></td><td>Bug p.index vs p.next di get_tl_program()</td><td>traci_client.py:301</td><td>Index fase tersimpan salah</td></tr>
</table>

<div class="fix-note"><strong>FIX 3.1:</strong> Cache tl_ids setelah lazy init, jangan panggil get_tl_ids() ulang. <strong>Effort: ~0.5 jam. GUI Engineer.</strong></div>
<div class="fix-note"><strong>FIX 3.2:</strong> Throttle update dashboard ke 4&ndash;5 Hz (gunakan counter atau QTimer terpisah). <strong>Effort: ~1 jam. GUI Engineer.</strong></div>
<div class="fix-note"><strong>FIX 3.3:</strong> Gunakan set difference: <code>gone = old_set - new_set</code>. <strong>Effort: ~1 jam. GUI Engineer.</strong></div>
<div class="fix-note"><strong>FIX 3.4:</strong> Ganti <code>p.next</code> jadi <code>p.index</code>. <strong>Effort: ~0.5 jam. Backend Engineer.</strong></div>

<!-- ==================== 8. PRIORITAS PERBAIKAN ==================== -->
<div class="page-break" id="s8"></div>
<h2>8. Prioritas Perbaikan &amp; Penanggung Jawab</h2>

<h3>8.1 Sprint 1: P1 &mdash; Critical (Estimasi 2&ndash;3 hari)</h3>
<table>
<tr><th>#</th><th>Tugas</th><th>Estimasi</th><th>File yang Diubah</th><th>Penanggung Jawab</th></tr>
<tr><td>1.1</td><td>Hapus loop Fuel/CO2; baca dari subscription atau hitung tiap 10 step</td><td>4 jam</td><td>traci_client.py, sim_controller.py</td><td><strong>Backend Engineer</strong></td></tr>
<tr><td>1.2</td><td>Ubah max_pressure pakai get_edge_data_cached()</td><td>3 jam</td><td>tl_algorithms.py</td><td><strong>Algorithm Engineer</strong></td></tr>
<tr><td>1.3</td><td>Bikin shared buffer thread-safe; pisahkan akses TraCI dari GUI</td><td>8 jam</td><td>traci_client.py, map_viewer.py, sim_controller.py</td><td><strong>Backend + GUI Engineer</strong></td></tr>
</table>

<h3>8.2 Sprint 2: P2 &mdash; High (Estimasi 2 hari)</h3>
<table>
<tr><th>#</th><th>Tugas</th><th>Estimasi</th><th>File yang Diubah</th><th>Penanggung Jawab</th></tr>
<tr><td>2.1</td><td>Unsubscribe kendaraan yang sudah keluar jaringan</td><td>3 jam</td><td>traci_client.py, sim_controller.py</td><td><strong>Backend Engineer</strong></td></tr>
<tr><td>2.2</td><td>Cache vehicle ID biar gak dobel panggil getIDList()</td><td>1 jam</td><td>traci_client.py</td><td><strong>Backend Engineer</strong></td></tr>
<tr><td>2.3</td><td>Perbaiki timing: actual_sleep = target - elapsed_body</td><td>2 jam</td><td>sim_controller.py</td><td><strong>Backend Engineer</strong></td></tr>
<tr><td>2.4</td><td>Tambah step_length ke pemanggilan step_single()</td><td>1 jam</td><td>sim_controller.py</td><td><strong>Backend Engineer</strong></td></tr>
</table>

<h3>8.3 Sprint 3: P3 &mdash; Medium (Estimasi 1 hari)</h3>
<table>
<tr><th>#</th><th>Tugas</th><th>Estimasi</th><th>File yang Diubah</th><th>Penanggung Jawab</th></tr>
<tr><td>3.1</td><td>Cache tl_ids setelah lazy init di map_viewer</td><td>0.5 jam</td><td>map_viewer.py</td><td><strong>GUI Engineer</strong></td></tr>
<tr><td>3.2</td><td>Throttle dashboard ke 4&ndash;5 Hz</td><td>1 jam</td><td>main_window.py</td><td><strong>GUI Engineer</strong></td></tr>
<tr><td>3.3</td><td>Pakai set difference untuk cleanup kendaraan</td><td>1 jam</td><td>map_viewer.py</td><td><strong>GUI Engineer</strong></td></tr>
<tr><td>3.4</td><td>Fix p.next &rarr; p.index di get_tl_program()</td><td>0.5 jam</td><td>traci_client.py</td><td><strong>Backend Engineer</strong></td></tr>
</table>

<h3>8.4 Ringkasan Penanggung Jawab</h3>
<table>
<tr><th>Peran</th><th>Nama (contoh)</th><th>Tanggung Jawab (P1/P2/P3)</th><th>Total Estimasi</th></tr>
<tr><td><strong>Backend Engineer</strong></td><td>&mdash;</td><td>1.1, 1.3 (bareng GUI), 2.1, 2.2, 2.3, 2.4, 3.4</td><td>~19.5 jam</td></tr>
<tr><td><strong>Algorithm Engineer</strong></td><td>&mdash;</td><td>1.2</td><td>~3 jam</td></tr>
<tr><td><strong>GUI Engineer</strong></td><td>&mdash;</td><td>1.3 (bareng Backend), 3.1, 3.2, 3.3</td><td>~10.5 jam</td></tr>
<tr><td><strong>QA / Tester</strong></td><td>&mdash;</td><td>Verifikasi setiap fix, regression test</td><td>~4 jam</td></tr>
<tr><td><strong>DevOps</strong></td><td>&mdash;</td><td>Build &amp; release setelah semua P1 selesai</td><td>~2 jam</td></tr>
</table>

<h3>8.5 Dampak yang Diharapkan Setelah Semua Fix</h3>
<table>
<tr><th>Metrik</th><th>Sebelum</th><th>Sesudah (estimasi)</th></tr>
<tr><td>Panggilan TraCI per step</td><td>~14.000+</td><td>~50&ndash;200</td></tr>
<tr><td>FPS GUI</td><td>8&ndash;12 (turun)</td><td>30 (stabil)</td></tr>
<tr><td>Thread safety</td><td>Crash acak</td><td>Stabil (shared buffer)</td></tr>
<tr><td>Memory (1 jam sim)</td><td>Terus bertambah</td><td>Stabil</td></tr>
<tr><td>Penyimpangan timing</td><td>Signifikan</td><td>&lt; 1%</td></tr>
</table>

<!-- ==================== 9. BUILD & DEPLOY ==================== -->
<div class="page-break" id="s9"></div>
<h2>9. Cara Build &amp; Deploy</h2>

<h3>9.1 Membuat Executable dengan PyInstaller</h3>
<p>PyInstaller mengemas aplikasi Python + semua library + data jadi satu file executable. Mirip membuat file .exe di Windows.</p>

<pre># Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller tls.spec --clean -y

# Hasil:
#   Linux:   dist/tls/tls
#   Windows: dist/tls/tls.exe
#   macOS:   dist/TLS.app/</pre>

<h3>9.2 Isi File tls.spec</h3>
<p><code>tls.spec</code> adalah resep untuk PyInstaller. Isinya:</p>
<ul>
<li><strong>Analysis:</strong> Daftar module Python yang perlu dibundel (traci, PyQt6, pyqtgraph, xml, json, csv, dll)</li>
<li><strong>Datas:</strong> Folder/data tambahan yang ikut dibundel (<code>sim/</code>, <code>resources/</code>, <code>README.md</code>)</li>
<li><strong>Excludes:</strong> Module yang tidak perlu (tkinter, matplotlib, OpenCV &mdash; menghemat ukuran)</li>
<li><strong>console=True:</strong> Menampilkan terminal di Windows (berguna untuk debug)</li>
<li><strong>BUNDLE:</strong> Khusus macOS &mdash; membuat .app bundle</li>
</ul>

<h3>9.3 Build Otomatis dengan GitHub Actions</h3>
<p>File <code>.github/workflows/build.yml</code> mendefinisikan pipeline CI/CD yang berjalan otomatis:</p>

<table>
<tr><th>Job</th><th>OS Runner</th><th>Aksi</th></tr>
<tr><td><strong>test</strong></td><td>ubuntu-latest</td><td>Install SUMO via apt, install Python deps, jalankan pytest</td></tr>
<tr><td><strong>build-linux</strong></td><td>ubuntu-latest</td><td>PyInstaller build + bundle SUMO binary + upload artifact</td></tr>
<tr><td><strong>build-windows</strong></td><td>windows-latest</td><td>PyInstaller build + download SUMO portable + bundle + upload artifact</td></tr>
<tr><td><strong>release</strong></td><td>ubuntu-latest</td><td>Download semua artifact, publish ke GitHub Releases</td></tr>
</table>

<p><strong>Pipeline ini berjalan saat:</strong></p>
<ul>
<li>Push ke branch <code>main</code> &rarr; menjalankan test + build (tanpa release)</li>
<li>Push tag <code>v*</code> (misal <code>v1.0.0</code>) &rarr; menjalankan test + build + release</li>
</ul>

<h3>9.4 Cara Membuat Release</h3>
<pre># 1. Pastikan semua sudah di-commit dan di-push
git status
git push origin main

# 2. Buat tag versi baru
git tag -a v1.0.0 -m "Release v1.0.0"

# 3. Push tag ke GitHub
git push origin v1.0.0

# 4. Buka https://github.com/Cefneal/traffic-light-sim/releases
#    Tunggu ~5-10 menit, artifact akan muncul otomatis</pre>

<h3>9.5 Strategi Bundling SUMO</h3>
<p>SUMO tidak dibundel ke dalam executable karena ukurannya terlalu besar (~200 MB) dan spesifik sistem operasi. Sebagai gantinya:</p>
<ul>
<li><strong>Linux:</strong> GitHub Actions install SUMO via apt, lalu copy binary <code>sumo</code> ke folder bundle</li>
<li><strong>Windows:</strong> GitHub Actions download SUMO portable zip dari sumo.dlr.de, extract ke folder bundle</li>
<li><strong>macOS:</strong> Belum otomatis &mdash; pengguna harus install via <code>brew install sumo</code></li>
</ul>
<p>Saat aplikasi dijalankan, ia mencari SUMO dengan urutan: (1) PATH, (2) SUMO_HOME, (3) lokasi instalasi umum (Windows: <code>C:\Program Files\SUMO\bin\</code>).</p>

<!-- ==================== 10. TESTING ==================== -->
<div class="page-break" id="s10"></div>
<h2>10. Strategi Testing</h2>

<h3>10.1 Jenis Test</h3>
<table>
<tr><th>Level</th><th>Lingkup</th><th>Tools</th><th>Frekuensi</th></tr>
<tr><td><strong>Unit Test</strong></td><td>Fungsi individu (algoritma TL, logika caching)</td><td>pytest</td><td>Setiap commit</td></tr>
<tr><td><strong>Integration Test</strong></td><td>SimController + TraCIClient (end-to-end 1 step)</td><td>pytest + SUMO</td><td>Setiap PR</td></tr>
<tr><td><strong>Performance Test</strong></td><td>Hitung jumlah panggilan TraCI per step, FPS</td><td>pytest-benchmark</td><td>Mingguan</td></tr>
<tr><td><strong>Regression Test</strong></td><td>TL behavior, dashboard update, export</td><td>pytest (headless)</td><td>Setiap P1 fix</td></tr>
</table>

<h3>10.2 Rencana Test Cases</h3>
<ul>
<li><strong>TestFixedTime:</strong> TL berpindah fase pada interval yang benar</li>
<li><strong>TestActuated:</strong> Detector memicu perpanjangan fase hijau</li>
<li><strong>TestMaxPressure:</strong> Fase dipilih berdasarkan beban edge tertinggi</li>
<li><strong>TestGreenWave:</strong> Offset fase dihitung dengan benar</li>
<li><strong>TestFuelMetrics:</strong> Nilai fuel/CO2 dalam rentang yang wajar</li>
<li><strong>TestThreadSafety:</strong> Tidak crash setelah 1000 step dengan GUI membaca bersamaan</li>
<li><strong>TestSubLeak:</strong> Jumlah subscription kendaraan stabil setelah warmup</li>
</ul>

<h3>10.3 Regression Test untuk Setiap Fix P1</h3>
<pre># 1. Smoke test: start sim, 100 step, stop
python -c "from tests.smoke import *; test_smoke()"

# 2. Bandingkan jumlah TraCI calls sebelum/sesudah
python -c "from tests.traci_count import *; compare_calls()"

# 3. Thread safety: loop 1000 step dengan GUI concurrent
python -c "from tests.thread_safety import *; test_no_crash(1000)"

# 4. Jalankan semua test
python -m pytest tests/ -v</pre>

<!-- ==================== 11. GLOSARIUM ==================== -->
<div class="page-break" id="s11"></div>
<h2>11. Glosarium Istilah Lengkap</h2>

<table>
<tr><th>Istilah</th><th>Arti</th></tr>
<tr><td><strong>Branch</strong></td><td>Cabang kode yang terpisah dari main. Digunakan untuk mengembangkan fitur tanpa mengganggu kode utama.</td></tr>
<tr><td><strong>CI/CD</strong></td><td>Continuous Integration / Continuous Deployment. Sistem otomatis yang menjalankan test &amp; build setiap kali kode di-push.</td></tr>
<tr><td><strong>Clone</strong></td><td>Mendownload seluruh riwayat proyek dari GitHub ke komputer lokal untuk pertama kali.</td></tr>
<tr><td><strong>Commit</strong></td><td>Merekam perubahan kode ke riwayat Git. Setiap commit punya pesan yang menjelaskan apa yang diubah.</td></tr>
<tr><td><strong>Controller</strong></td><td>Bagian dari MVC yang mengatur logika aplikasi (di sini: SimController).</td></tr>
<tr><td><strong>Dashboard</strong></td><td>Panel grafik real-time yang menampilkan metrik simulasi (kecepatan, throughput, dll).</td></tr>
<tr><td><strong>Dependency</strong></td><td>Library Python yang dibutuhkan aplikasi (tercantum di requirements.txt).</td></tr>
<tr><td><strong>Detector / Induction Loop</strong></td><td>Sensor di jalan yang mendeteksi kendaraan. Digunakan oleh algoritma Actuated.</td></tr>
<tr><td><strong>Edge</strong></td><td>Ruas jalan di SUMO. Setiap edge punya data: jumlah kendaraan, kecepatan rata-rata, dll.</td></tr>
<tr><td><strong>Executable</strong></td><td>File binary yang bisa dijalankan langsung tanpa perlu Python terinstall (misal: .exe di Windows).</td></tr>
<tr><td><strong>Fase (Phase)</strong></td><td>Status lampu lalu lintas pada suatu waktu, misal: "gggrrr" = 3 lajur hijau + 3 lajur merah.</td></tr>
<tr><td><strong>FPS</strong></td><td>Frames Per Second. Seberapa sering GUI memperbarui tampilan (target: 30).</td></tr>
<tr><td><strong>GitHub Actions</strong></td><td>Layanan CI/CD bawaan GitHub. Otomatis build &amp; test saat push.</td></tr>
<tr><td><strong>GUI</strong></td><td>Graphical User Interface. Tampilan visual aplikasi (jendela, tombol, peta).</td></tr>
<tr><td><strong>Import OSM</strong></td><td>Mengunduh data peta dari OpenStreetMap dan mengonversinya ke format SUMO.</td></tr>
<tr><td><strong>Merge</strong></td><td>Menggabungkan perubahan dari satu branch ke branch lain.</td></tr>
<tr><td><strong>Model</strong></td><td>Bagian dari MVC yang mengelola data (di sini: TraCIClient).</td></tr>
<tr><td><strong>MVC</strong></td><td>Model-View-Controller. Pola arsitektur yang memisahkan data, logika, dan tampilan.</td></tr>
<tr><td><strong>Pull</strong></td><td>Mengambil perubahan terbaru dari GitHub ke komputer lokal.</td></tr>
<tr><td><strong>Pull Request (PR)</strong></td><td>Permintaan untuk menggabungkan kode dari branch fitur ke branch main. Biasanya direview dulu.</td></tr>
<tr><td><strong>Push</strong></td><td>Mengirim commit lokal ke GitHub.</td></tr>
<tr><td><strong>PyInstaller</strong></td><td>Tools untuk mengubah aplikasi Python jadi standalone executable.</td></tr>
<tr><td><strong>Race Condition</strong></td><td>Dua thread mengakses data yang sama bersamaan &rarr; hasil tidak terduga / crash.</td></tr>
<tr><td><strong>Rebase</strong></td><td>Memindahkan commit branch ke ujung branch lain. Alternatif merge yang menghasilkan riwayat lebih rapi.</td></tr>
<tr><td><strong>Remote</strong></td><td>Server Git jarak jauh (biasanya <code>origin</code> = GitHub).</td></tr>
<tr><td><strong>Signal / PyQt6 Signal</strong></td><td>Mekanisme komunikasi thread-safe di PyQt6. Sim thread kirim signal, GUI thread terima &amp; proses.</td></tr>
<tr><td><strong>Stash</strong></td><td>Menyimpan perubahan sementara agar bisa pindah branch tanpa commit.</td></tr>
<tr><td><strong>Step / Simulation Step</strong></td><td>Satu iterasi simulasi (default: 1 detik simulasi).</td></tr>
<tr><td><strong>Subscription</strong></td><td>Fitur TraCI: berlangganan data tertentu (posisi kendaraan, status TL, dll) agar otomatis diterima setiap step tanpa diminta.</td></tr>
<tr><td><strong>SUMO</strong></td><td>Simulation of Urban MObility. Engine simulasi lalu lintas open-source dari DLR Jerman.</td></tr>
<tr><td><strong>Tag</strong></td><td>Penanda versi di Git. Biasanya untuk rilis (v1.0.0, v1.1.0, dll).</td></tr>
<tr><td><strong>Thread</strong></td><td>Unit eksekusi paralel. TLS punya 2 thread: sim (perhitungan) dan GUI (tampilan).</td></tr>
<tr><td><strong>TL</strong></td><td>Traffic Light. Lampu lalu lintas.</td></tr>
<tr><td><strong>TraCI</strong></td><td>Traffic Control Interface. Protokol TCP untuk mengontrol SUMO dari Python.</td></tr>
<tr><td><strong>Venv</strong></td><td>Virtual Environment. Lingkungan Python terisolasi agar library gak bentrok.</td></tr>
<tr><td><strong>View</strong></td><td>Bagian dari MVC yang menampilkan data ke pengguna (di sini: MapViewer, Dashboard).</td></tr>
<tr><td><strong>Wheel</strong></td><td>Format distribusi Python pre-built. Lebih cepat install daripada kompilasi dari source.</td></tr>
</table>

<!-- ==================== 12. LAMPIRAN ==================== -->
<div class="page-break" id="s12"></div>
<h2>12. Lampiran: Referensi File Penting</h2>

<h3>12.1 Layer Engine (Model + Controller)</h3>
<table>
<tr><th>File</th><th>Isi Penting</th><th>Baris</th></tr>
<tr><td>app/engine/traci_client.py</td><td>TraCIClient: connect, subscribe, cached reads, TL control, fuel/CO2</td><td>499</td></tr>
<tr><td>app/engine/sim_controller.py</td><td>SimController: start, stop, _run_loop, step_single, emit signal</td><td>298</td></tr>
<tr><td>app/engine/tl_algorithms.py</td><td>4 algoritma: fixed, actuated, max_pressure, green_wave</td><td>173</td></tr>
<tr><td>app/engine/osm_importer.py</td><td>Konversi file .osm ke .net.xml via netconvert</td><td>~80</td></tr>
</table>

<h3>12.2 Layer GUI (View)</h3>
<table>
<tr><th>File</th><th>Isi Penting</th><th>Baris</th></tr>
<tr><td>app/gui/main_window.py</td><td>MainWindow: layout, menu bar, signal bridge, sim lifecycle</td><td>233</td></tr>
<tr><td>app/gui/map_viewer.py</td><td>MapViewer: render jaringan, kendaraan, TL, heatmap, tile OSM</td><td>674</td></tr>
<tr><td>app/gui/dashboard.py</td><td>DashboardPanel: pyqtgraph chart, export CSV/JSON</td><td>181</td></tr>
<tr><td>app/gui/controls.py</td><td>ControlsToolbar: play/pause/stop, speed, scenario dropdown</td><td>~150</td></tr>
</table>

<h3>12.3 Layer Data (Metrics + Models)</h3>
<table>
<tr><th>File</th><th>Isi Penting</th><th>Baris</th></tr>
<tr><td>app/metrics/collector.py</td><td>MetricsCollector: ring buffer, record, summary stats</td><td>83</td></tr>
<tr><td>app/metrics/storage.py</td><td>StorageManager: SQLite + JSON persistence</td><td>~130</td></tr>
<tr><td>app/models/traffic_light.py</td><td>TLPhase, TrafficLight: fase, durasi, elapsed time</td><td>~40</td></tr>
<tr><td>app/models/vehicle.py</td><td>Vehicle: posisi, kecepatan, sudut, tipe</td><td>~30</td></tr>
</table>

<h3>12.4 File Setup &amp; Build</h3>
<table>
<tr><th>File</th><th>Fungsi</th></tr>
<tr><td>setup.bat</td><td>Setup untuk Windows CMD (create venv, install deps, cek SUMO)</td></tr>
<tr><td>setup.ps1</td><td>Setup untuk Windows PowerShell (sama, tapi lebih reliable)</td></tr>
<tr><td>setup.sh</td><td>Setup untuk Linux / macOS (detect brew, apt)</td></tr>
<tr><td>tls.spec</td><td>Resep PyInstaller: module, data, konfigurasi build</td></tr>
<tr><td>requirements.txt</td><td>Daftar dependency Python (PyQt6, pyqtgraph, traci, weasyprint)</td></tr>
<tr><td>.github/workflows/build.yml</td><td>Pipeline CI/CD: test &rarr; build Linux &rarr; build Windows &rarr; release</td></tr>
<tr><td>scripts/generate_docs_pdf.py</td><td>Script pembuat PDF dokumentasi ini</td></tr>
</table>

<h3>12.5 Struktur Folder sim/ (Data Map)</h3>
<table>
<tr><th>Map</th><th>Lokasi</th><th>Keterangan</th></tr>
<tr><td>Pamulang</td><td>sim/pamulang/</td><td>Kawasan Pamulang, Tangerang Selatan, Indonesia. ~15 TL.</td></tr>
<tr><td>Silicon Valley</td><td>sim/silicon_valley/</td><td>San Jose &amp; sekitarnya, California, USA. ~77 TL.</td></tr>
<tr><td>Tokyo</td><td>sim/tokyo/</td><td>Shibuya &amp; Shinjuku, Tokyo, Japan. ~100+ TL.</td></tr>
</table>
<p>Setiap folder map berisi:</p>
<ul>
<li><code>*.net.xml</code> &mdash; Jaringan jalan + TL (dihasilkan oleh netconvert)</li>
<li><code>*.rou.xml</code> &mdash; Rute kendaraan (kendaraan + perjalanan)</li>
<li><code>*.sumocfg</code> &mdash; Konfigurasi SUMO (menggabungkan .net.xml + .rou.xml)</li>
<li><code>buildings.json</code> &mdash; Data bangunan untuk tampilan visual (opsional)</li>
</ul>

<p class="center small" style="margin-top:40px;">
&mdash; Akhir Dokumen &mdash;<br>
Dibuat oleh generate_docs_pdf.py | TLS v1.0.0 | Bahasa Indonesia
</p>

</body>
</html>
"""

# Generate PDF
weasyprint.HTML(string=HTML).write_pdf(str(OUTPUT))
print(f"PDF generated: {OUTPUT}")
print(f"Size: {OUTPUT.stat().st_size / 1024:.1f} KB")
