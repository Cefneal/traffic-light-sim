#!/usr/bin/env python3
"""
Setup all preset maps: Pamulang, Silicon Valley, Tokyo.
Downloads OSM from bounding boxes, converts with netconvert,
generates vehicle routes, creates .sumocfg.
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
SIM_DIR = PROJECT_DIR / "sim"

MAPS = [
    {
        "name": "pamulang",
        "bbox": (106.718, -6.360, 106.768, -6.315),
        "duration": 1800,
        "period": 1.0,
        "flow": 1800,
    },
    {
        "name": "silicon_valley",
        "bbox": (-121.898, 37.332, -121.880, 37.350),
        "duration": 1800,
        "period": 1.2,
        "flow": 1500,
    },
    {
        "name": "tokyo",
        "bbox": (139.697, 35.656, 139.708, 35.667),
        "duration": 1800,
        "period": 1.0,
        "flow": 2000,
    },
]

VEHICLE_DIST = [
    ("car", 0.55),
    ("motor", 0.25),
    ("truck", 0.08),
    ("bus", 0.05),
    ("angkot", 0.07),
]

USER_AGENT = "TLS-App/1.0 (traffic-light-sim; educational)"


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def download_osm(name: str, bbox: tuple, out_path: Path) -> bool:
    if out_path.exists() and out_path.stat().st_size > 1000:
        log(f"  {name}: OSM already exists, skipping download")
        return True

    left, bottom, right, top = bbox
    url = f"https://www.openstreetmap.org/api/0.6/map?bbox={left},{bottom},{right},{top}"
    log(f"  {name}: Downloading from {left},{bottom},{right},{top}...")

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        out_path.write_bytes(data)
        log(f"  {name}: Downloaded {len(data)} bytes")
        return True
    except Exception as e:
        log(f"  {name}: Download failed: {e}")
        return False


def run_netconvert(name: str, osm_path: Path, net_path: Path) -> bool:
    if net_path.exists() and net_path.stat().st_size > 1000:
        log(f"  {name}: Network already exists, skipping")
        return True

    netconvert_bin = os.environ.get("NETCONVERT_BIN", "netconvert")
    cmd = [
        netconvert_bin,
        "--osm-files", str(osm_path),
        "--output-file", str(net_path),
        "--geometry.remove",
        "--roundabouts.guess",
        "--ramps.guess",
        "--junctions.join",
        "--tls.guess-signals",
        "--tls.discard-simple",
        "--tls.default-type", "actuated",
    ]
    log(f"  {name}: Running netconvert...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            log(f"  {name}: netconvert failed: {result.stderr[:300]}")
            return False
        log(f"  {name}: Network created ({net_path.stat().st_size} bytes)")
        return True
    except subprocess.TimeoutExpired:
        log(f"  {name}: netconvert timed out")
        return False


def get_net_stats(net_path: Path) -> dict:
    try:
        tree = ET.parse(str(net_path))
        root = tree.getroot()
        nodes = len(root.findall(".//junction"))
        edges = len(root.findall(".//edge"))
        tls = len(root.findall(".//tlLogic"))
        return {"nodes": nodes, "edges": edges, "tls": tls}
    except Exception:
        return {"nodes": 0, "edges": 0, "tls": 0}


def generate_routes(name: str, net_path: Path, routes_path: Path,
                    duration: int, period: float, flow: int) -> bool:
    if routes_path.exists() and routes_path.stat().st_size > 1000:
        log(f"  {name}: Routes already exist, skipping")
        return True

    try:
        import traci
        tools_dir = Path(traci.__file__).resolve().parent.parent / "tools"
    except ImportError:
        log(f"  {name}: traci not available, can't find randomTrips.py")
        return False

    rand_trips = tools_dir / "randomTrips.py"
    if not rand_trips.exists():
        log(f"  {name}: randomTrips.py not found at {rand_trips}")
        return False

    # Generate base routes
    cmd = [
        sys.executable, str(rand_trips),
        "-n", str(net_path),
        "-o", str(routes_path),
        "--begin", "0",
        "--end", str(duration),
        "--period", str(period),
        "-r", str(flow),
        "--validate",
    ]
    log(f"  {name}: Generating routes ({duration}s, period={period})...")
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        log(f"  {name}: Routes generated ({routes_path.stat().st_size} bytes)")
        return True
    except subprocess.TimeoutExpired:
        log(f"  {name}: randomTrips.py timed out")
        return False


def create_sumocfg(name: str, out_dir: Path, duration: int, net_file: str,
                   routes_file: str) -> Path:
    cfg_path = out_dir / "test.sumocfg"
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="{net_file}"/>
        <route-files value="{routes_file}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="{duration}"/>
    </time>
    <processing>
        <time-to-teleport value="120"/>
    </processing>
</configuration>
"""
    cfg_path.write_text(content)
    log(f"  {name}: Config created ({cfg_path})")
    return cfg_path


def setup_map(m: dict) -> bool:
    name = m["name"]
    bbox = m["bbox"]
    duration = m["duration"]

    out_dir = SIM_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)

    osm_path = out_dir / "input.osm"
    net_path = out_dir / "network.net.xml"
    routes_path = out_dir / "routes.xml"

    log(f"\n{'='*50}")
    log(f"Setting up: {name}")

    # Step 1: Download OSM
    if not download_osm(name, bbox, osm_path):
        log(f"  {name}: FAILED at download")
        return False

    # Step 2: Convert to SUMO network
    if not run_netconvert(name, osm_path, net_path):
        log(f"  {name}: FAILED at netconvert")
        return False

    # Step 3: Show network stats
    stats = get_net_stats(net_path)
    log(f"  {name}: {stats['nodes']} nodes, {stats['edges']} edges, {stats['tls']} TLs")

    if stats["tls"] == 0:
        log(f"  {name}: WARNING — no traffic lights detected!")

    # Step 4: Generate routes
    period = m["period"]
    flow = m["flow"]
    if not generate_routes(name, net_path, routes_path, duration, period, flow):
        log(f"  {name}: FAILED at route generation")
        return False

    # Step 5: Create .sumocfg
    create_sumocfg(name, out_dir, duration, "network.net.xml", "routes.xml")

    log(f"  {name}: ✅ Done! ({stats['tls']} TLs, {stats['edges']} edges)")
    return True


def main():
    log("Starting map setup...")
    log(f"SIM_DIR = {SIM_DIR}")
    log(f"Python = {sys.executable}")

    # Check netconvert
    netconvert_bin = os.environ.get("NETCONVERT_BIN", "netconvert")
    try:
        subprocess.run([netconvert_bin, "--version"], capture_output=True)
    except FileNotFoundError:
        log(f"ERROR: '{netconvert_bin}' not found. Install SUMO first.")
        sys.exit(1)

    success = 0
    failed = 0
    for m in MAPS:
        if setup_map(m):
            success += 1
        else:
            failed += 1

    log(f"\n{'='*50}")
    log(f"Summary: {success} succeeded, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
