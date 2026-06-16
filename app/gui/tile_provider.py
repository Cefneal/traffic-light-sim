from __future__ import annotations

import math
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

from app.utils.qt_compat import QPointF, QRectF, QPixmap

from app.utils.logger import get_logger


TILE_SERVERS: dict[str, dict[str, str]] = {
    "street": {
        "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        "attribution": "© OpenStreetMap contributors",
    },
    "satellite": {
        "url": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        "attribution": "© Google",
    },
    "hybrid": {
        "url": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        "attribution": "© Google",
    },
    "terrain": {
        "url": "https://tile.opentopomap.org/{z}/{x}/{y}.png",
        "attribution": "© OpenTopoMap",
    },
}

CACHE_DIR = Path.home() / ".tls" / "tiles"
TILE_SIZE = 256


class TileProvider:
    def __init__(self) -> None:
        self.logger = get_logger("tiles")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._last_request = 0.0

    # ── Coordinate conversion ─────────────────────────────────

    @staticmethod
    def lonlat_to_tilexy(lon: float, lat: float, zoom: int) -> tuple[int, int]:
        n = 2 ** zoom
        x_tile = int((lon + 180.0) / 360.0 * n)
        lat_rad = math.radians(lat)
        y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return x_tile, y_tile

    @staticmethod
    def tilexy_to_bounds(
        x: int, y: int, zoom: int,
    ) -> tuple[float, float, float, float]:
        n = 2 ** zoom
        lon_min = x / n * 360.0 - 180.0
        lon_max = (x + 1) / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1.0 - 2.0 * y / n)))
        lat_max = math.degrees(lat_rad)
        lat_rad = math.atan(math.sinh(math.pi * (1.0 - 2.0 * (y + 1) / n)))
        lat_min = math.degrees(lat_rad)
        return lon_min, lat_min, lon_max, lat_max

    # ── Download / cache ──────────────────────────────────────

    def get_tile(
        self, x: int, y: int, zoom: int, style: str = "street",
    ) -> Optional[QPixmap]:
        cache_path = CACHE_DIR / style / str(zoom) / str(x)
        cache_path.mkdir(parents=True, exist_ok=True)
        file_path = cache_path / f"{y}.png"

        if file_path.exists():
            pix = QPixmap(str(file_path))
            if not pix.isNull():
                return pix

        server = TILE_SERVERS.get(style)
        if not server:
            return None

        url = server["url"].format(z=zoom, x=x, y=y)

        elapsed = time.time() - self._last_request
        if elapsed < 0.3:
            time.sleep(0.3 - elapsed)

        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "TLS-TrafficLightSim/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
            self._last_request = time.time()
            file_path.write_bytes(data)
            pix = QPixmap(str(file_path))
            if not pix.isNull():
                return pix
        except (urllib.error.URLError, OSError) as e:
            self.logger.warning(f"Tile download failed {url}: {e}")

        return None

    def get_attribution(self, style: str) -> str:
        server = TILE_SERVERS.get(style)
        return server["attribution"] if server else ""

    # ── Zoom helpers ──────────────────────────────────────────

    @staticmethod
    def pick_zoom(
        lon_span: float, lat_span: float, target_tiles: int = 8,
    ) -> int:
        for z in range(20, 0, -1):
            n = 2 ** z
            tiles_x = max(1, lon_span / (360.0 / n))
            tiles_y = max(1, lat_span / (180.0 / n))
            if tiles_x * tiles_y <= target_tiles * 2:
                return z
        return 16

    @staticmethod
    def sumo_to_latlon(
        sx: float, sy: float,
        conv_min: tuple[float, float],
        conv_max: tuple[float, float],
        orig_min: tuple[float, float],
        orig_max: tuple[float, float],
    ) -> tuple[float, float]:
        lon = (sx - conv_min[0]) / (conv_max[0] - conv_min[0])
        lon = lon * (orig_max[0] - orig_min[0]) + orig_min[0]
        lat = (sy - conv_min[1]) / (conv_max[1] - conv_min[1])
        lat = lat * (orig_max[1] - orig_min[1]) + orig_min[1]
        return lon, lat

    @staticmethod
    def latlon_to_sumo(
        lon: float, lat: float,
        conv_min: tuple[float, float],
        conv_max: tuple[float, float],
        orig_min: tuple[float, float],
        orig_max: tuple[float, float],
    ) -> tuple[float, float]:
        sx = (lon - orig_min[0]) / (orig_max[0] - orig_min[0])
        sx = sx * (conv_max[0] - conv_min[0]) + conv_min[0]
        sy = (lat - orig_min[1]) / (orig_max[1] - orig_min[1])
        sy = sy * (conv_max[1] - conv_min[1]) + conv_min[1]
        return sx, sy
