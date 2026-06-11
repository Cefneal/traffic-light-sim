#!/usr/bin/env python3
"""
Extract building footprints from an OSM file and save as buildings.json
in the same directory, using projection from the corresponding .net.xml.

Usage:
    python scripts/extract_buildings.py sim/tokyo/input.osm
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_projection(net_path: str) -> dict:
    tree = ET.parse(net_path)
    loc = tree.getroot().find("location")
    if loc is None:
        return {}
    cb = loc.get("convBoundary", "")
    ob = loc.get("origBoundary", "")
    if not cb or not ob:
        return {}
    parts = [float(v) for v in cb.split(",")]
    conv_min = (parts[0], parts[1])
    conv_max = (parts[2], parts[3])
    parts = [float(v) for v in ob.split(",")]
    orig_min = (parts[0], parts[1])
    orig_max = (parts[2], parts[3])
    return {
        "conv_min": conv_min,
        "conv_max": conv_max,
        "orig_min": orig_min,
        "orig_max": orig_max,
    }


def latlon_to_sumo(
    lon: float, lat: float,
    proj: dict,
) -> tuple[float, float]:
    conv_min = proj["conv_min"]
    conv_max = proj["conv_max"]
    orig_min = proj["orig_min"]
    orig_max = proj["orig_max"]
    sx = (lon - orig_min[0]) / (orig_max[0] - orig_min[0])
    sx = sx * (conv_max[0] - conv_min[0]) + conv_min[0]
    sy = (lat - orig_min[1]) / (orig_max[1] - orig_min[1])
    sy = sy * (conv_max[1] - conv_min[1]) + conv_min[1]
    return sx, sy


def extract_buildings(osm_path: str) -> list[dict]:
    tree = ET.parse(osm_path)
    root = tree.getroot()

    nodes: dict[str, tuple[float, float]] = {}
    for node in root.findall("node"):
        nodes[node.get("id")] = (
            float(node.get("lon", 0)),
            float(node.get("lat", 0)),
        )

    ways: dict[str, list[str]] = {}
    way_tags: dict[str, dict[str, str]] = {}
    for way in root.findall("way"):
        wid = way.get("id")
        refs = [nd.get("ref") for nd in way.findall("nd")]
        ways[wid] = refs
        tags = {}
        for tag in way.findall("tag"):
            tags[tag.get("k")] = tag.get("v")
        way_tags[wid] = tags

    buildings = []
    for wid, tags in way_tags.items():
        if "building" not in tags:
            continue
        refs = ways.get(wid, [])
        if len(refs) < 3:
            continue
        corners = []
        for ref in refs:
            if ref in nodes:
                corners.append(nodes[ref])
        if len(corners) >= 3:
            buildings.append({
                "id": wid,
                "type": tags.get("building", "yes"),
                "height": float(str(tags.get("height", "10")).replace("m", "")),
                "corners": corners,
            })

    return buildings


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_buildings.py <input.osm>")
        sys.exit(1)

    osm_path = Path(sys.argv[1])
    if not osm_path.exists():
        print(f"File not found: {osm_path}")
        sys.exit(1)

    osm_dir = osm_path.parent
    net_path = osm_dir / "network.net.xml"

    if not net_path.exists():
        print(f"net.xml not found at {net_path}, looking for alternatives...")
        for f in osm_dir.glob("*.net.xml"):
            net_path = f
            break
        if not net_path.exists():
            print("No .net.xml found. Buildings will use raw lat/lon.")
            proj = {}
        else:
            proj = parse_projection(str(net_path))
    else:
        proj = parse_projection(str(net_path))

    raw = extract_buildings(str(osm_path))
    print(f"Found {len(raw)} buildings")

    out_path = osm_dir / "buildings.json"

    if proj:
        converted = []
        for b in raw:
            sumo_corners = []
            for lon, lat in b["corners"]:
                sx, sy = latlon_to_sumo(lon, lat, proj)
                sumo_corners.append([sx, sy])
            converted.append({
                "id": b["id"],
                "type": b["type"],
                "height": b["height"],
                "corners": sumo_corners,
            })
        with open(out_path, "w") as f:
            json.dump(converted, f, indent=2)
        print(f"Saved {len(converted)} converted buildings to {out_path}")
    else:
        with open(out_path, "w") as f:
            json.dump(raw, f, indent=2)
        print(f"Saved {len(raw)} raw buildings to {out_path}")


if __name__ == "__main__":
    main()
