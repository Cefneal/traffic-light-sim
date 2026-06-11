#!/usr/bin/env python3
"""Post-process SUMO .net.xml: add proper traffic lights to major junctions.

Generates tlLogic elements with correct phase state string lengths
based on the actual number of controlled connections at each junction.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def count_int_lanes(junction) -> int:
    lanes_str = junction.get("intLanes", "")
    return len([l for l in lanes_str.split() if l.strip()])


def count_connections(junction) -> int:
    """Count incoming lanes — each gets a signal state char."""
    inc = junction.get("incLanes", "")
    return max(1, len([l for l in inc.split() if l.strip()]))


def add_tls_to_network(net_path: str, output_path: str | None = None,
                        min_lanes: int = 8) -> int:
    tree = ET.parse(net_path)
    root = tree.getroot()

    existing_tl_ids = {tl.get("id") for tl in root.findall(".//tlLogic")}
    tl_junction_ids = {
        j.get("id") for j in root.findall(".//junction[@type='traffic_light']")
    }

    to_convert: list[ET.Element] = []
    for j in root.findall(".//junction[@type='priority']"):
        jid = j.get("id", "")
        if jid in tl_junction_ids:
            continue
        if count_int_lanes(j) >= min_lanes:
            to_convert.append(j)

    if not to_convert:
        print(f"  No new junctions (existing: {len(existing_tl_ids)} TLs)")
        return 0

    max_tl_id = 0
    for tl in root.findall(".//tlLogic"):
        try:
            max_tl_id = max(max_tl_id, int(tl.get("id", "0")))
        except ValueError:
            pass

    added = 0
    for j in to_convert:
        max_tl_id += 1
        tl_id = str(max_tl_id)
        j.set("type", "traffic_light")

        n_inc = count_connections(j)
        n_inc = max(1, min(32, n_inc))

        tl_logic = ET.SubElement(root, "tlLogic")
        tl_logic.set("id", tl_id)
        tl_logic.set("type", "actuated")
        tl_logic.set("programID", "0")
        tl_logic.set("offset", "0")

        half = n_inc // 2
        r = "r"
        g = "g"
        y = "y"

        # Simple 2-phase pattern with all-red
        phase_defs = [
            # Phase 0: first half green, rest red
            (g * half + r * (n_inc - half), 30),
            # Phase 0 yellow
            (y * half + r * (n_inc - half), 4),
            # Phase 1: second half green, first half red
            (r * half + g * (n_inc - half), 30),
            # Phase 1 yellow
            (r * half + y * (n_inc - half), 4),
            # All red
            (r * n_inc, 2),
        ]

        for p_state, p_dur in phase_defs:
            p_state = p_state[:n_inc]
            phase_el = ET.SubElement(tl_logic, "phase")
            phase_el.set("duration", str(p_dur))
            phase_el.set("state", p_state)

        added += 1

    out = output_path or net_path
    tree.write(out, encoding="utf-8", xml_declaration=True)
    print(f"  Added {added} TLs ({out.name if hasattr(out,'name') else out})")

    final_tls = len(root.findall(".//tlLogic"))
    final_tl_juncs = len(root.findall(".//junction[@type='traffic_light']"))
    print(f"  Total: {final_tls} TLs, {final_tl_juncs} TL junctions")
    return added


def main():
    project_dir = Path(__file__).resolve().parent.parent
    configs = [
        ("Pamulang", "sim/pamulang/network.net.xml", 8),
        ("Silicon Valley", "sim/silicon_valley/network.net.xml", 10),
        ("Tokyo", "sim/tokyo/network.net.xml", 12),
    ]

    total = 0
    for name, rel_path, min_lanes in configs:
        net_path = project_dir / rel_path
        if not net_path.exists():
            print(f"Skipping {name}")
            continue
        print(f"\n--- {name} (min_lanes={min_lanes}) ---")
        added = add_tls_to_network(str(net_path), min_lanes=min_lanes)
        total += added

    print(f"\nTotal TLs added: {total}")


if __name__ == "__main__":
    main()
