#!/usr/bin/env python3
"""Generate comprehensive TLS Documentation PDF via weasyprint"""

from pathlib import Path
import weasyprint

OUTPUT = Path(__file__).resolve().parent.parent / "TLS-Documentation.pdf"

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 2cm 1.8cm;
    @bottom-center {{
        content: counter(page);
        font: 9px Helvetica;
        color: #888;
    }}
}}
body {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: 10px;
    line-height: 1.5;
    color: #333;
}}
h1 {{
    font-size: 28px;
    color: #fff;
    background: #2e84c4;
    padding: 12px 20px;
    margin: 0;
}}
h2 {{
    font-size: 16px;
    color: #2e84c4;
    border-bottom: 2px solid #2e84c4;
    padding-bottom: 4px;
    margin: 20px 0 10px;
}}
h3 {{
    font-size: 12px;
    color: #2c3e50;
    margin: 14px 0 6px;
}}
h4 {{
    font-size: 10px;
    color: #555;
    margin: 10px 0 4px;
}}
.cover {{
    text-align: center;
    padding-top: 120px;
}}
.cover h1 {{
    font-size: 48px;
    background: none;
    color: #2e84c4;
    padding: 0;
}}
.cover .subtitle {{
    font-size: 18px; color: #666; margin: 8px 0;
}}
.cover .meta {{
    margin-top: 50px; font-size: 11px; color: #888;
}}
.cover .meta p {{ margin: 3px 0; }}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 9px;
}}
th {{
    background: #2e84c4;
    color: #fff;
    padding: 5px 6px;
    text-align: left;
    font-weight: bold;
}}
td {{
    padding: 4px 6px;
    border: 1px solid #ddd;
}}
tr:nth-child(even) td {{
    background: #f5f7fa;
}}
pre {{
    background: #282c34;
    color: #e0e0e0;
    padding: 8px 12px;
    border-radius: 4px;
    font: 8px/1.4 "Courier New", monospace;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-word;
}}
ul {{ padding-left: 20px; }}
li {{ margin: 2px 0; }}
.note {{
    background: #fef9e7;
    border-left: 3px solid #e67e22;
    padding: 6px 10px;
    margin: 8px 0;
    font-size: 9px;
}}
.fix-note {{
    background: #e8f8f5;
    border-left: 3px solid #2ecc71;
    padding: 6px 10px;
    margin: 8px 0;
    font-size: 9px;
}}
.toc a {{ color: #333; text-decoration: none; }}
.toc a:hover {{ text-decoration: underline; }}
.page-break {{ page-break-before: always; }}
.small {{ font-size: 8px; color: #999; }}
</style>
</head>
<body>

<!-- ═══════════════════════ COVER ═══════════════════════ -->
<div class="cover">
<h1>TLS</h1>
<p class="subtitle">Traffic Light Simulation</p>
<p style="font-size:13px; color:#999;">Comprehensive Documentation &amp; Performance Analysis</p>
<div class="meta">
<p>Version 1.0.0</p>
<p>Engine: SUMO 1.27 + TraCI</p>
<p>GUI: PyQt6 &middot; Charts: pyqtgraph</p>
<p>Platform: Linux / Windows / macOS</p>
<p>Python 3.10 &ndash; 3.13</p>
</div>
</div>

<!-- ═══════════════════════ TOC ═══════════════════════ -->
<div class="page-break"></div>
<h2>Table of Contents</h2>
<ol class="toc">
<li><a href="#s1">Project Overview</a></li>
<li><a href="#s2">Tech Stack</a></li>
<li><a href="#s3">Project Structure</a></li>
<li><a href="#s4">Quick Start</a></li>
<li><a href="#s5">Git Workflow &amp; Contribution</a></li>
<li><a href="#s6">Code Architecture (MVC)</a></li>
<li><a href="#s7">Performance Analysis</a></li>
<li><a href="#s8">Bottleneck Deep Dive</a></li>
<li><a href="#s9">Fix Priority &amp; Responsibility</a></li>
<li><a href="#s10">Build &amp; Deploy</a></li>
<li><a href="#s11">Test Strategy</a></li>
<li><a href="#s12">Appendix: Key File Reference</a></li>
</ol>

<!-- ═══════════════════════ 1 ═══════════════════════ -->
<div class="page-break" id="s1"></div>
<h2>1. Project Overview</h2>
<p>TLS (Traffic Light Simulation) is a desktop application for city-scale traffic simulation using the <strong>SUMO</strong> (Simulation of Urban MObility) engine. It provides a real-time interactive GUI with multiple traffic light algorithms, live metrics dashboard, and OSM map import support.</p>

<h3>Key Features</h3>
<ul>
<li>3 built-in map presets: Pamulang (Indonesia), Silicon Valley (USA), Tokyo (Japan)</li>
<li>4 traffic light algorithms: Fixed-Time, Actuated, Green Wave, Max-Pressure</li>
<li>Real-time dashboard: avg speed, wait time, throughput, queue length, fuel, CO₂</li>
<li>OSM import: download any city from OpenStreetMap and simulate instantly</li>
<li>CSV / JSON export for post-analysis</li>
<li>Multi-platform: Linux, Windows, macOS (via Python + PyQt6)</li>
</ul>

<h3>Problem Statement</h3>
<p>Traditional traffic light timing is static and inefficient, causing congestion, fuel waste, and pollution. TLS enables researchers and city planners to test adaptive TL algorithms (Actuated, Max-Pressure, Green Wave) against real-world or synthetic traffic scenarios before deployment.</p>

<h3>Target Audience</h3>
<ul>
<li>Traffic engineers evaluating adaptive signal control</li>
<li>Researchers studying urban mobility</li>
<li>Students learning SUMO/TraCI simulation</li>
<li>City planners comparing scenarios</li>
</ul>

<!-- ═══════════════════════ 2 ═══════════════════════ -->
<div class="page-break" id="s2"></div>
<h2>2. Tech Stack</h2>
<p>TLS is built on a Python foundation with a real-time coupling to the SUMO traffic simulator via the TraCI protocol. The GUI layer uses PyQt6 with pyqtgraph for live charting.</p>

<table>
<tr><th>Component</th><th>Technology</th><th>Version</th></tr>
<tr><td>Simulation Engine</td><td>SUMO (via TraCI)</td><td>1.20+ (1.27 tested)</td></tr>
<tr><td>GUI Framework</td><td>PyQt6</td><td>&gt;= 6.5</td></tr>
<tr><td>Real-time Charts</td><td>pyqtgraph</td><td>&gt;= 0.13</td></tr>
<tr><td>PDF Export (optional)</td><td>weasyprint</td><td>&gt;= 60</td></tr>
<tr><td>Language</td><td>CPython</td><td>3.10 - 3.13</td></tr>
<tr><td>Database</td><td>SQLite (stdlib)</td><td>built-in</td></tr>
<tr><td>OS (Dev)</td><td>Ubuntu 22.04 / Windows 11</td><td>&mdash;</td></tr>
</table>

<h3>Why SUMO?</h3>
<p>SUMO is the de-facto open-source traffic simulation engine (DLR, since 2001). It supports large-scale networks (entire cities), multi-modal transport, emission modeling, and TraCI &mdash; a TCP-based protocol for real-time control. TLS uses TraCI to step the simulation, query vehicle positions, and set traffic light phases on every step.</p>

<h3>Why PyQt6?</h3>
<p>PyQt6 provides native desktop performance with hardware-accelerated rendering (QGraphicsView for the map, QTimer-based animation loop). pyqtgraph leverages PyQt6&rsquo;s OpenGL support for smooth real-time chart updates at 30+ FPS.</p>

<h3>Python 3.14 Warning</h3>
<p>Python 3.14 <strong>does not have wheels</strong> for PyQt6 or pyqtgraph yet. The setup scripts (setup.bat, setup.ps1, setup.sh) will warn if Python 3.14 is detected. Use Python 3.10&ndash;3.13.</p>

<!-- ═══════════════════════ 3 ═══════════════════════ -->
<div class="page-break" id="s3"></div>
<h2>3. Project Structure</h2>
<p>The project follows a clean MVC-like layout within <code>app/</code>, with simulation data under <code>sim/</code> and utilities under <code>scripts/</code>:</p>

<pre>traffic-light-sim/
+-- app/
|   +-- main.py                         Entry point
|   +-- engine/
|   |   +-- traci_client.py             TraCI wrapper (Model)
|   |   +-- sim_controller.py           Simulation loop (Controller)
|   |   +-- tl_algorithms.py            TL algorithm functions
|   |   +-- osm_importer.py             OSM -&gt; SUMO netimport
|   +-- gui/
|   |   +-- map_viewer.py              Map + vehicles + TL (QGraphicsView)
|   |   +-- main_window.py             Window layout, menus, signals
|   |   +-- dashboard.py               Real-time charts (pyqtgraph)
|   |   +-- controls.py                Play/Pause/Speed toolbar
|   |   +-- config_panel.py            Algorithm config panel
|   |   +-- settings_dialog.py         App settings
|   |   +-- scenario_dialog.py         Save/load scenarios
|   |   +-- tile_provider.py           OSM tile background
|   +-- models/
|   |   +-- traffic_light.py           TLPhase, TrafficLight dataclasses
|   |   +-- vehicle.py                 Vehicle dataclass
|   +-- metrics/
|   |   +-- collector.py               MetricsCollector (ring buffer)
|   |   +-- storage.py                 SQLite/JSON persistence
|   +-- utils/
|       +-- config.py                  Config manager (JSON file)
|       +-- localization.py            i18n (id_ID, en_US)
|       +-- logger.py                  Loguru wrapper
+-- sim/
|   +-- pamulang/                      Pamulang map data
|   +-- silicon_valley/                Silicon Valley map data
|   +-- tokyo/                         Tokyo map data
+-- scripts/
|   +-- setup_maps.py                  Initialize map folders
|   +-- generate_logo.py               Generate icon.png + icon.ico
|   +-- generate_docs_pdf.py           This PDF generator
|   +-- add_tls_to_network.py          Utility for TL placement
+-- tests/                             (pending)
+-- .github/workflows/build.yml        CI/CD pipeline
+-- setup.bat                          Windows (CMD) setup
+-- setup.ps1                          Windows (PowerShell) setup
+-- setup.sh                           Linux/macOS setup
+-- tls.spec                           PyInstaller spec
+-- requirements.txt                   Python dependencies
+-- README.md                          Project readme</pre>

<!-- ═══════════════════════ 4 ═══════════════════════ -->
<div class="page-break" id="s4"></div>
<h2>4. Quick Start</h2>

<h3>Prerequisites</h3>
<ul>
<li>Python 3.10 &ndash; 3.13 (<strong>3.14 NOT supported</strong> &mdash; no PyQt6 wheels)</li>
<li>SUMO 1.20+ installed and in PATH (or set <code>SUMO_HOME</code> env var)</li>
</ul>

<h3>Clone &amp; Setup</h3>
<pre># Linux / macOS
git clone https://github.com/Cefneal/traffic-light-sim.git
cd traffic-light-sim
bash setup.sh
source venv/bin/activate && python -m app.main

# Windows (PowerShell - recommended)
git clone https://github.com/Cefneal/traffic-light-sim.git
cd traffic-light-sim
.\\setup.ps1
.\\venv\\Scripts\\Activate.ps1 ; python -m app.main

# Windows (CMD)
setup.bat
venv\\Scripts\\activate & python -m app.main</pre>

<h3>Pre-built Executable</h3>
<p>Download from <a href="https://github.com/Cefneal/traffic-light-sim/releases">GitHub Releases</a> (auto-built via GitHub Actions on every tag push):</p>
<pre># Linux
wget https://github.com/Cefneal/traffic-light-sim/releases/latest/download/TLS-Linux-x64.tar.gz
tar xzf TLS-Linux-x64.tar.gz
cd TLS-Linux-x64 && ./tls

# Windows - download TLS-Windows-x64.zip from Releases, extract and run tls.exe</pre>
<div class="note">NOTE: SUMO must still be installed separately &mdash; it is too large to bundle (~200 MB).</div>

<!-- ═══════════════════════ 5 ═══════════════════════ -->
<div class="page-break" id="s5"></div>
<h2>5. Git Workflow &amp; Contribution</h2>

<h3>Branching Strategy</h3>
<p>The project follows a simplified trunk-based development on <code>main</code> with feature branches:</p>
<ul>
<li><code>main</code> &mdash; Stable, always deployable. Protected branch.</li>
<li><code>feature/*</code> &mdash; For new features and fixes. Merge via PR.</li>
<li><code>fix/*</code> &mdash; For urgent hotfixes (P1 items).</li>
</ul>

<h3>Daily Workflow</h3>
<pre># 1. Pull latest
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/my-fix

# 3. Work, commit frequently
git add app/engine/sim_controller.py
git commit -m "fix: reduce TraCI calls in simulation loop"

# 4. Push branch
git push -u origin feature/my-fix

# 5. Create PR on GitHub, get reviewed
# 6. Merge to main after approval</pre>

<h3>Commit Message Convention</h3>
<table>
<tr><th>Prefix</th><th>Meaning</th><th>Example</th></tr>
<tr><td><code>fix:</code></td><td>Bug fix</td><td>fix: race condition in TraCI thread access</td></tr>
<tr><td><code>feat:</code></td><td>New feature</td><td>feat: add OSM import dialog</td></tr>
<tr><td><code>perf:</code></td><td>Performance</td><td>perf: cache vehicle subscription results</td></tr>
<tr><td><code>docs:</code></td><td>Documentation</td><td>docs: add Windows setup instructions</td></tr>
<tr><td><code>refactor:</code></td><td>Code change</td><td>refactor: extract TL building logic</td></tr>
<tr><td><code>chore:</code></td><td>Maintenance</td><td>chore: update requirements.txt pins</td></tr>
</table>

<h3>Tagging &amp; Release</h3>
<p>Tags trigger automated builds via GitHub Actions:</p>
<pre># List tags
git tag -l

# Create and push a new release tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# This triggers .github/workflows/build.yml:
#   - Test: pytest on linux-latest
#   - Build Linux: PyInstaller + bundle SUMO binaries
#   - Build Windows: PyInstaller + download SUMO portable
#   - Release: Upload all artifacts to GitHub Releases</pre>

<h3>GitHub Actions Pipeline</h3>
<p>The CI/CD pipeline (<code>.github/workflows/build.yml</code>) has 4 jobs:</p>
<ul>
<li><strong>test</strong> &mdash; Runs pytest on ubuntu-latest with SUMO installed via apt</li>
<li><strong>build-linux</strong> &mdash; PyInstaller build, bundles SUMO binaries, uploads artifact</li>
<li><strong>build-windows</strong> &mdash; Uses windows-latest runner, downloads SUMO portable zip, bundles</li>
<li><strong>release</strong> &mdash; On tag push, publishes all artifacts to GitHub Releases</li>
</ul>

<!-- ═══════════════════════ 6 ═══════════════════════ -->
<div class="page-break" id="s6"></div>
<h2>6. Code Architecture (MVC)</h2>
<p>TLS follows a classic Model-View-Controller pattern:</p>
<ul>
<li><strong>Model</strong> &mdash; <code>TraCIClient</code> wraps all TraCI calls, manages subscriptions, caches data</li>
<li><strong>Controller</strong> &mdash; <code>SimController</code> runs the simulation loop in a daemon thread</li>
<li><strong>View</strong> &mdash; PyQt6 widgets (<code>MapViewer</code>, <code>DashboardPanel</code>, <code>ControlsToolbar</code>)</li>
</ul>

<pre>  +------------------+     PyQt6 signals     +------------------+
  |  SimController   | -------------------&gt; |   MapViewer      |
  |  (Controller)    |                       |   DashboardPanel |
  |  daemon thread   |     emits step        |   ControlsBar    |
  +--------+---------+     every 33ms         +-----------------+
           |
     owns  |  (model layer)
           v
  +------------------+     TCP loopback
  |  TraCIClient     | &lt;====&gt; SUMO (TraCI)
  |  (Model)         |       port 8813
  +------------------+</pre>

<h3>6.1 TraCIClient (Model)</h3>
<p>Located in <code>app/engine/traci_client.py</code> (499 lines). Wraps all TraCI calls and provides subscription-based cached access.</p>
<p><strong>Key design decisions:</strong></p>
<ul>
<li><strong>Subscriptions:</strong> Edges, vehicles, and traffic lights are subscribed once (or incrementally) so that after each <code>simulationStep()</code>, cached data can be read with zero additional TraCI socket calls.</li>
<li><strong>Caches:</strong> <code>_cached_tl_ids</code> stores TL IDs to avoid repeated <code>getIDList()</code> calls.</li>
<li><strong>Thread-unsafe (ISSUE):</strong> All methods call <code>traci.*</code> directly without locks. This is the #1 cause of <code>setPhase failed</code> errors when the GUI thread reads while the sim thread writes.</li>
</ul>

<pre># CORRECT usage (sim thread only):
tc.subscribe_edges(all_edges)       # one-time
tc.simulation_step()                # advances SUMO
data = tc.get_edge_data_cached(eid) # zero socket calls

# WRONG (causes 14,000+ calls/step):
tc.get_total_fuel_consumption()     # loops all vehicles!</pre>

<h3>6.2 SimController (Controller)</h3>
<p>Located in <code>app/engine/sim_controller.py</code> (298 lines). Runs the simulation loop in a daemon thread.</p>
<p><strong>Responsibilities:</strong></p>
<ul>
<li>Start/stop/pause/resume simulation (SUMO process lifecycle)</li>
<li>Step timing: calls <code>simulation_step()</code>, dispatches TL algorithms, collects metrics</li>
<li>Event system: emits <code>step</code>, <code>start</code>, <code>stop</code> events to GUI listeners via PyQt6 signals</li>
</ul>

<pre># Simulation loop (sim_controller.py:179-248)
while self._running:
    if not self._paused:
        veh_ids = self.traci.get_vehicle_ids()
        self.traci.subscribe_vehicles(veh_ids)  # BUG: leaks subscriptions
        self.traci.simulation_step()
        self._algorithm_fn(tl, traci, sim_time) # dispatches TL algo
        self.collector.record(...)
        self._emit('step', data)
    time.sleep(1.0 / (30 * speed))             # BUG: no drift correction</pre>

<h3>6.3 GUI (View)</h3>
<p>Three main widgets update independently:</p>
<ul>
<li><strong>MapViewer</strong> (674 lines): QGraphicsView with QTimer-based animation loop at ~30 FPS. Renders vehicles, roads, junctions, TL lights, trails, heatmap, OSM tiles.</li>
<li><strong>DashboardPanel</strong> (181 lines): pyqtgraph PlotWidget with rolling time-series charts (speed, wait time, throughput, queue, fuel, CO₂).</li>
<li><strong>ControlsToolbar</strong> (~150 lines): Play, Pause, Stop, Speed slider, scenario dropdown.</li>
</ul>

<h3>6.4 Data Flow Per Step</h3>
<table>
<tr><th>Step</th><th>Thread</th><th>Action</th><th>TraCI Calls</th></tr>
<tr><td>1</td><td>Sim</td><td>get_vehicle_ids() + subscribe_vehicles()</td><td>2+</td></tr>
<tr><td>2</td><td>Sim</td><td>simulationStep() &mdash; advances SUMO 1 step</td><td>1</td></tr>
<tr><td>3</td><td>Sim</td><td>get_all_vehicles_cached() &mdash; reads subscription</td><td>0</td></tr>
<tr><td>4</td><td>Sim</td><td>get_total_fuel_consumption() &mdash; loops ALL vehicles</td><td>N*2</td></tr>
<tr><td>5</td><td>Sim</td><td>TL algorithms &mdash; edge calls, setPhase</td><td>10-1500</td></tr>
<tr><td>6</td><td>Sim</td><td>Emit 'step' signal to GUI</td><td>0</td></tr>
<tr><td>7</td><td>GUI</td><td>get_all_vehicles_cached() &mdash; reads subscription</td><td>0+</td></tr>
<tr><td>8</td><td>GUI</td><td>get_cached_tl_state() per TL &mdash; subscription</td><td>0</td></tr>
</table>

<!-- ═══════════════════════ 7 ═══════════════════════ -->
<div class="page-break" id="s7"></div>
<h2>7. Performance Analysis</h2>
<p>This section identifies all performance bottlenecks categorized by severity. The TraCI protocol communicates over TCP loopback &mdash; each call has ~100&micro;s latency. With <strong>14,000+ calls per step</strong> and a 30 FPS target, the simulation spends most of its time waiting for TraCI responses rather than computing.</p>

<h3>P1 - Critical (must fix immediately)</h3>
<p>These issues cause significant lag, crashes, or incorrect behavior. They block basic usability.</p>
<table>
<tr><th>#</th><th>Issue</th><th>Location</th><th>Impact</th><th>Calls/Step</th></tr>
<tr><td>1.1</td><td>Fuel/CO₂ loop per vehicle</td><td>traci_client.py:401-423</td><td>N vehicles x 2 calls/step</td><td>~10,000</td></tr>
<tr><td>1.2</td><td>MaxPressure edge query loop</td><td>tl_algorithms.py:84-116</td><td>N edges x N phases x N TLs</td><td>~1,500</td></tr>
<tr><td>1.3</td><td>Thread race condition (GUI+SIM)</td><td>sim_controller + map_viewer</td><td>Crash: "setPhase failed / Connection closed"</td><td>N/A</td></tr>
</table>

<h3>P2 - High (should fix soon)</h3>
<table>
<tr><th>#</th><th>Issue</th><th>Location</th><th>Impact</th><th>Calls/Step</th></tr>
<tr><td>2.1</td><td>Vehicle subscription leak</td><td>sim_controller.py:189-192</td><td>SUMO slows progressively; memory grows</td><td>N/A</td></tr>
<tr><td>2.2</td><td>Double getIDList() call</td><td>sim_controller + traci_client</td><td>Redundant ID fetch per step</td><td>~2</td></tr>
<tr><td>2.3</td><td>Sleep-based timing drift</td><td>sim_controller.py:245-246</td><td>Real-time sync degrades over time</td><td>0</td></tr>
<tr><td>2.4</td><td>step_single missing step_length arg</td><td>sim_controller.py:259</td><td>actuated_controller gap_timer broken</td><td>0</td></tr>
</table>

<h3>P3 - Medium (nice to have)</h3>
<table>
<tr><th>#</th><th>Issue</th><th>Location</th><th>Impact</th><th>Calls/Step</th></tr>
<tr><td>3.1</td><td>TL get_tl_ids called twice per frame</td><td>map_viewer.py:526,543</td><td>Double ID fetch per GUI update</td><td>~2</td></tr>
<tr><td>3.2</td><td>Dashboard chart re-render 30 Hz</td><td>main_window.py:114-128</td><td>CPU waste on chart updates</td><td>0</td></tr>
<tr><td>3.3</td><td>Vehicle cleanup full dict scan O(n)</td><td>map_viewer.py:508-519</td><td>Loop over all items every frame</td><td>0</td></tr>
<tr><td>3.4</td><td>p.index vs p.next bug in get_tl_program</td><td>traci_client.py:301</td><td>Wrong phase index stored</td><td>0</td></tr>
</table>

<div class="note">Total estimated impact: ~14,000+ TraCI calls/step before fixes &rarr; ~50-200 after fixes. FPS should stabilize at 30 from 8-12.</div>

<!-- ═══════════════════════ 8 ═══════════════════════ -->
<div class="page-break" id="s8"></div>
<h2>8. Bottleneck Deep Dive</h2>

<h3>8.1 Fuel/CO₂ Loop (P1 #1.1)</h3>
<p>The <code>get_total_fuel_consumption()</code> and <code>get_total_co2_emission()</code> methods each iterate over all vehicle IDs and call <code>getFuelConsumption(vid)</code> / <code>getCO2Emission(vid)</code> individually. With 5,000 vehicles, this is 10,000 TraCI calls per step. At 30 FPS, this is 300,000 calls/second.</p>
<pre># traci_client.py:401-423
def get_total_fuel_consumption(self) -> float:
    total = 0.0
    for vid in traci.vehicle.getIDList():        # 5000 ids
        total += traci.vehicle.getFuelConsumption(vid)  # 5000 calls
    return total

# Called every step in sim_controller.py:208-209
total_fuel = self.traci.get_total_fuel_consumption()  # 5000 calls
total_co2 = self.traci.get_total_co2_emission()       # 5000 calls</pre>
<div class="fix-note"><strong>FIX:</strong> Add VAR_FUELCONSUMPTION and VAR_CO2EMISSION to the vehicle subscription variables list. Then read from subscription results instead. Alternatively, compute fuel/CO₂ only every 10th step since they change slowly.</div>

<h3>8.2 Max-Pressure Edge Query (P1 #1.2)</h3>
<p>The max_pressure_controller queries edge data for every TL phase individually instead of using the already-subscribed edge data:</p>
<pre># tl_algorithms.py:96-108
edge_ids = traci_module.edge.getIDList()[:50]    # 1 call
for i, phase in enumerate(tl.phases):            # ~3 phases
    for eid in edge_ids:                         # ~50 edges
        count = traci_module.edge.getLastStepVehicleNumber(eid)  # 1 call
        speed = traci_module.edge.getLastStepMeanSpeed(eid)      # 1 call
    # Total per TL: 1 + 3 * 50 * 2 = 301 calls per TL</pre>
<p>With ~10 TLs, max_pressure alone accounts for ~3,000 calls/step.</p>
<div class="fix-note"><strong>FIX:</strong> Use <code>get_edge_data_cached(eid)</code> which reads from the subscription results instead of making new TraCI calls. Edge data is already subscribed in <code>sim_controller.py:164-165</code>.</div>

<h3>8.3 Thread Race Condition (P1 #1.3)</h3>
<p>This is the most critical &mdash; and the hardest to reproduce &mdash; bug. Two threads access the same TraCI connection simultaneously:</p>
<pre># THREAD 1: SimController._run_loop (sim thread)
self.traci.simulation_step()          # TraCI: SimulationStep command
  # during this call, the socket is in use

# THREAD 2: MapViewer._update_view (GUI thread, ~30 Hz)
vehicles = tc.get_all_vehicles_cached()  # TraCI: getIDList + subscription results
  # This fires while Thread 1 has the socket locked!

# Result:
#   - "setPhase failed: Connection already closed"
#   - Random crashes
#   - GUI freezes waiting for TraCI lock</pre>
<div class="fix-note"><strong>FIX:</strong> Implement a thread-safe data exchange pattern. The sim thread writes vehicle/TL data to a shared buffer protected by <code>threading.Lock</code>. The GUI thread reads from this buffer. <strong>Never touch traci.* from the GUI thread.</strong></div>

<h3>8.4 Vehicle Subscription Leak (P2 #2.1)</h3>
<p>Every step, the simulation loop subscribes to all current vehicle IDs. Vehicles that leave the network are never unsubscribed:</p>
<pre># sim_controller.py:189-192
veh_ids = self.traci.get_vehicle_ids()
self.traci.subscribe_vehicles(veh_ids)

# traci_client.py:158-167
new_vids = [vid for vid in vehicle_ids if vid not in self._subscribed_vehicles]
for vid in new_vids:
    traci.vehicle.subscribe(vid, ...)    # ADD but never REMOVE
    self._subscribed_vehicles.add(vid)   # grows unbounded!</pre>
<p>Over a 1-hour simulation with 10,000 unique vehicles passing through, SUMO accumulates 10,000 active subscriptions &mdash; each processed on every <code>simulationStep()</code>, causing progressive slowdown.</p>
<div class="fix-note"><strong>FIX:</strong> After each step, compute set difference: gone = subscribed - current_ids, then unsubscribe gone vehicles via <code>traci.vehicle.unsubscribe(vid)</code>.</div>

<!-- ═══════════════════════ 9 ═══════════════════════ -->
<div class="page-break" id="s9"></div>
<h2>9. Fix Priority &amp; Responsibility</h2>
<p>Fixes should be implemented in priority order. Each P1 fix is independent and can be done in parallel.</p>

<h3>Sprint 1: P1 - Critical (estimated 2-3 days)</h3>
<table>
<tr><th>#</th><th>Task</th><th>Effort</th><th>Files</th><th>Owner</th></tr>
<tr><td>1.1</td><td>Remove Fuel/CO₂ loop; read from subscription or compute every 10 steps</td><td>4h</td><td>traci_client.py, sim_controller.py</td><td>Backend</td></tr>
<tr><td>1.2</td><td>Rewrite max_pressure to use get_edge_data_cached()</td><td>3h</td><td>tl_algorithms.py</td><td>Algorithm</td></tr>
<tr><td>1.3</td><td>Add threading.Lock around TraCI; buffer vehicle/TL data for GUI</td><td>8h</td><td>traci_client.py, map_viewer.py</td><td>Backend+GUI</td></tr>
</table>

<h3>Sprint 2: P2 - High (estimated 2 days)</h3>
<table>
<tr><th>#</th><th>Task</th><th>Effort</th><th>Files</th><th>Owner</th></tr>
<tr><td>2.1</td><td>Unsubscribe vehicles that have left the network</td><td>3h</td><td>traci_client.py, sim_controller.py</td><td>Backend</td></tr>
<tr><td>2.2</td><td>Cache vehicle IDs to avoid double getIDList()</td><td>1h</td><td>traci_client.py</td><td>Backend</td></tr>
<tr><td>2.3</td><td>Fix sleep timing: actual_sleep = target - elapsed_body_time</td><td>2h</td><td>sim_controller.py</td><td>Backend</td></tr>
<tr><td>2.4</td><td>Add missing step_length arg to step_single()</td><td>1h</td><td>sim_controller.py</td><td>Backend</td></tr>
</table>

<h3>Sprint 3: P3 - Medium (estimated 1 day)</h3>
<table>
<tr><th>#</th><th>Task</th><th>Effort</th><th>Files</th><th>Owner</th></tr>
<tr><td>3.1</td><td>Cache tl_ids after lazy init in map_viewer</td><td>0.5h</td><td>map_viewer.py</td><td>GUI</td></tr>
<tr><td>3.2</td><td>Throttle dashboard updates to 4-5 Hz (use QTimer or counter)</td><td>1h</td><td>main_window.py</td><td>GUI</td></tr>
<tr><td>3.3</td><td>Use set difference for vehicle cleanup (gone = old - new)</td><td>1h</td><td>map_viewer.py</td><td>GUI</td></tr>
<tr><td>3.4</td><td>Fix p.next -&gt; p.index in get_tl_program()</td><td>0.5h</td><td>traci_client.py</td><td>Backend</td></tr>
</table>

<h3>Expected Impact After Fixes</h3>
<table>
<tr><th>Metric</th><th>Before</th><th>After (estimated)</th></tr>
<tr><td>TraCI calls per step</td><td>~14,000+</td><td>~50-200</td></tr>
<tr><td>GUI FPS (1000 vehicles)</td><td>8-12 (adaptive)</td><td>30 (stable)</td></tr>
<tr><td>Thread safety</td><td>Crashes</td><td>Stable with shared buffer</td></tr>
<tr><td>Memory (1h simulation)</td><td>Growing (sub leak)</td><td>Stable</td></tr>
<tr><td>Sim timing drift</td><td>Significant</td><td>&lt; 1% error</td></tr>
</table>

<!-- ═══════════════════════ 10 ═══════════════════════ -->
<div class="page-break" id="s10"></div>
<h2>10. Build &amp; Deploy</h2>

<h3>PyInstaller Executable</h3>
<p>TLS uses PyInstaller to create a standalone executable. The spec file (<code>tls.spec</code>) bundles the app, simulation data, resources, and all Python dependencies into a single binary.</p>
<pre># Install PyInstaller
pip install pyinstaller

# Build
pyinstaller tls.spec --clean -y

# Output:
#   dist/tls/tls          (Linux)
#   dist/tls/tls.exe      (Windows)
#   dist/TLS.app/         (macOS, if sys.platform == 'darwin')</pre>

<h3>GitHub Actions Automation</h3>
<p>The <code>.github/workflows/build.yml</code> runs on every push to main and on tag push (v*):</p>
<pre># Pipeline (simplified):
jobs:
  test:         pytest on ubuntu-latest (with SUMO via apt)
  build-linux:  PyInstaller + bundle SUMO binaries
  build-windows: PyInstaller + download SUMO portable zip
  release:      Upload artifacts to GitHub Releases

# To trigger a release:
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0</pre>

<h3>SUMO Bundling Strategy</h3>
<p>The executables do NOT bundle SUMO (~200 MB, system-dependent):</p>
<ul>
<li><strong>Linux:</strong> Workflow installs sumo via apt, copies bin/sumo to the bundle</li>
<li><strong>Windows:</strong> Workflow downloads SUMO portable zip (official), extracts to bundle</li>
<li><strong>macOS:</strong> Requires <code>brew install sumo</code> (not bundled yet)</li>
</ul>

<p>The app searches for SUMO in: PATH, SUMO_HOME, and uses <code>shutil.which()</code> for reliable detection on all platforms.</p>

<h3>tls.spec Notes</h3>
<ul>
<li><code>console=True</code>: Shows a terminal window on Windows for debug output</li>
<li><code>BUNDLE</code> block is macOS-only (conditional on <code>sys.platform == 'darwin'</code>)</li>
<li><code>upx=True</code>: Compresses the executable with UPX (reduces size ~30%)</li>
<li>Hidden imports include all TraCI domain modules, PyQt6 submodules, xml/json/csv</li>
</ul>

<!-- ═══════════════════════ 11 ═══════════════════════ -->
<div class="page-break" id="s11"></div>
<h2>11. Test Strategy</h2>

<h3>Test Levels</h3>
<table>
<tr><th>Level</th><th>Scope</th><th>Tool</th><th>Frequency</th></tr>
<tr><td>Unit</td><td>Individual functions (TraCI wrapper, algorithms)</td><td>pytest</td><td>Every commit</td></tr>
<tr><td>Integration</td><td>SimController + TraCIClient (end-to-end step)</td><td>pytest + SUMO</td><td>Every PR</td></tr>
<tr><td>Performance</td><td>TraCI calls/step count, FPS benchmark</td><td>pytest-benchmark</td><td>Weekly</td></tr>
<tr><td>Regression</td><td>TL behavior, dashboard update, export</td><td>pytest (headless)</td><td>On P1 fix</td></tr>
</table>

<h3>Planned Test Cases</h3>
<ul>
<li><code>TestFixedTime</code>: TL switches phase at correct intervals</li>
<li><code>TestActuated</code>: Detector triggers extension logic</li>
<li><code>TestMaxPressure</code>: Phase selected based on edge load</li>
<li><code>TestGreenWave</code>: Phase sync offset calculation</li>
<li><code>TestFuelMetrics</code>: Fuel/CO₂ values within expected range</li>
<li><code>TestThreadSafety</code>: No crashes after 1000 steps with concurrent GUI reads</li>
<li><code>TestSubLeak</code>: Subscribed vehicle count stabilizes after warmup</li>
</ul>

<h3>Regression Test After Each P1 Fix</h3>
<pre># 1. Smoke test: start sim, run 100 steps, stop
python -c "from tests.smoke import *; test_smoke()"

# 2. Metric comparison: TraCI calls before/after
python -c "from tests.traci_count import *; compare_calls()"

# 3. Thread safety: loop with concurrent GUI reads
python -c "from tests.thread_safety import *; test_no_crash(1000)"

# 4. Full test suite
python -m pytest tests/ -v</pre>

<!-- ═══════════════════════ 12 ═══════════════════════ -->
<div class="page-break" id="s12"></div>
<h2>12. Appendix: Key File Reference</h2>

<h3>Engine Layer</h3>
<table>
<tr><th>File</th><th>Key Classes/Functions</th><th>Lines</th></tr>
<tr><td>traci_client.py</td><td>TraCIClient: connect, subscribe, cached reads, TL control</td><td>499</td></tr>
<tr><td>sim_controller.py</td><td>SimController: start, stop, _run_loop, step_single</td><td>298</td></tr>
<tr><td>tl_algorithms.py</td><td>fixed/actuated/max_pressure/green_wave + _switch_to_next</td><td>173</td></tr>
<tr><td>osm_importer.py</td><td>OSMImporter: convert .osm to .net.xml via netconvert</td><td>~80</td></tr>
</table>

<h3>GUI Layer</h3>
<table>
<tr><th>File</th><th>Key Classes/Functions</th><th>Lines</th></tr>
<tr><td>main_window.py</td><td>MainWindow: layout, menus, signal bridge, sim lifecycle</td><td>233</td></tr>
<tr><td>map_viewer.py</td><td>MapViewer: network rendering, vehicles, TL, heatmap, tiles</td><td>674</td></tr>
<tr><td>dashboard.py</td><td>DashboardPanel: pyqtgraph charts, CSV/JSON export</td><td>181</td></tr>
<tr><td>controls.py</td><td>ControlsToolbar: play/pause/stop, speed, scenario selector</td><td>~150</td></tr>
</table>

<h3>Metrics &amp; Models</h3>
<table>
<tr><th>File</th><th>Key Classes/Functions</th><th>Lines</th></tr>
<tr><td>collector.py</td><td>MetricsCollector: ring buffer, record, summary stats</td><td>83</td></tr>
<tr><td>storage.py</td><td>StorageManager: SQLite + JSON persistence</td><td>~130</td></tr>
<tr><td>traffic_light.py</td><td>TLPhase, TrafficLight: phase state, elapsed time</td><td>~40</td></tr>
<tr><td>vehicle.py</td><td>Vehicle: position, speed, angle, type dataclass</td><td>~30</td></tr>
</table>

<h3>Setup &amp; Config</h3>
<table>
<tr><th>File</th><th>Purpose</th></tr>
<tr><td>setup.bat</td><td>Windows CMD setup script</td></tr>
<tr><td>setup.ps1</td><td>Windows PowerShell setup script (recommended)</td></tr>
<tr><td>setup.sh</td><td>Linux/macOS setup script</td></tr>
<tr><td>tls.spec</td><td>PyInstaller spec for building executables</td></tr>
<tr><td>requirements.txt</td><td>Python dependency list</td></tr>
<tr><td>.github/workflows/build.yml</td><td>CI/CD pipeline configuration</td></tr>
<tr><td>README.md</td><td>Project documentation (quick start, troubleshooting)</td></tr>
</table>

<p style="text-align:center; color:#999; margin-top:40px; font-size:9px;">
&mdash; End of Document &mdash;<br>
Generated by generate_docs_pdf.py | TLS v1.0.0
</p>

</body>
</html>
"""

# Generate PDF
weasyprint.HTML(string=HTML).write_pdf(str(OUTPUT))
print(f"PDF generated: {OUTPUT}")
print(f"Size: {OUTPUT.stat().st_size / 1024:.1f} KB")
