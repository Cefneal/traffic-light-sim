"""
OSM Importer

Wraps SUMO's netconvert tool to convert OpenStreetMap files to SUMO networks.
"""

from __future__ import annotations
import os
import subprocess
import tempfile
from typing import Optional

from app.utils.logger import get_logger


class OSMImporter:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger("osm")

    def import_osm(self, osm_path: str, output_dir: Optional[str] = None) -> str:
        if not os.path.exists(osm_path):
            raise FileNotFoundError(f"OSM file not found: {osm_path}")

        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="tls_osm_")

        base_name = os.path.splitext(os.path.basename(osm_path))[0]
        net_path = os.path.join(output_dir, f"{base_name}.net.xml")

        if os.path.exists(net_path):
            self.logger.info(f"Network already exists: {net_path}")
            return net_path

        netconvert_bin = self.config.get_netconvert_binary()
        cmd = [
            netconvert_bin,
            "--osm-files", osm_path,
            "--output-file", net_path,
            "--geometry.remove",
            "--roundabouts.guess",
            "--ramps.guess",
            "--junctions.join",
            "--tls.guess-signals",
            "--tls.discard-simple",
            "--tls.default-type", "actuated",
        ]

        self.logger.info(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"netconvert failed:\n{result.stderr[:500]}"
                )
            self.logger.info(f"Network created: {net_path}")
            return net_path
        except subprocess.TimeoutExpired:
            raise RuntimeError("netconvert timed out after 300s")

    def import_from_url(self, url: str, output_dir: Optional[str] = None) -> str:
        import urllib.request
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="tls_osm_")
        os.makedirs(output_dir, exist_ok=True)
        osm_path = os.path.join(output_dir, "input.osm")
        self.logger.info(f"Downloading OSM from {url}")
        urllib.request.urlretrieve(url, osm_path)
        return self.import_osm(osm_path, output_dir)

    def parse_network_info(self, net_path: str) -> dict:
        import xml.etree.ElementTree as ET
        info = {"nodes": 0, "edges": 0, "traffic_lights": 0, "bounds": None}
        try:
            tree = ET.parse(net_path)
            root = tree.getroot()
            info["nodes"] = len(root.findall(".//junction"))
            info["edges"] = len(root.findall(".//edge"))
            info["traffic_lights"] = len(root.findall(".//tlLogic"))
            loc = root.find(".//location")
            if loc is not None:
                attr = loc.attrib.get("convBoundary", "")
                if attr:
                    parts = [float(x) for x in attr.split(",")]
                    if len(parts) == 4:
                        info["bounds"] = tuple(parts)
        except ET.ParseError as e:
            self.logger.warning(f"Failed to parse network XML: {e}")
        return info
