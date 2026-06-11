"""
Map Viewer Widget

Renders road network, vehicles, and traffic lights using QGraphicsView.
Updates in real-time during simulation.
"""

import math
import time
from collections import deque

from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem, QLabel,
)
from PyQt6.QtCore import Qt, QRectF, QTimer, QPointF
from PyQt6.QtGui import QPolygonF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QFont, QPixmap

from app.gui.tile_provider import TileProvider
from app.utils.logger import get_logger

logger = get_logger("map_viewer")


DARK_COLORS = {
    "road": QColor(60, 60, 80),
    "road_bg": QColor(40, 40, 55),
    "vehicle_car": QColor(52, 152, 219),
    "vehicle_truck": QColor(230, 126, 34),
    "vehicle_bus": QColor(241, 196, 15),
    "vehicle_emergency": QColor(231, 76, 60),
    "tl_green": QColor(46, 204, 113),
    "tl_yellow": QColor(241, 196, 15),
    "tl_red": QColor(231, 76, 60),
    "tl_off": QColor(100, 100, 100),
    "heatmap_low": QColor(46, 204, 113, 60),
    "heatmap_med": QColor(241, 196, 15, 80),
    "heatmap_high": QColor(231, 76, 60, 100),
    "background": QColor(26, 26, 46),
    "grid": QColor(50, 50, 70),
    "junction": QColor(80, 80, 110),
    "junction_pen": QColor(100, 100, 130),
}

LIGHT_COLORS = {
    "road": QColor(160, 160, 170),
    "road_bg": QColor(220, 220, 215),
    "vehicle_car": QColor(41, 128, 185),
    "vehicle_truck": QColor(211, 84, 0),
    "vehicle_bus": QColor(212, 172, 13),
    "vehicle_emergency": QColor(192, 57, 43),
    "tl_green": QColor(39, 174, 96),
    "tl_yellow": QColor(212, 172, 13),
    "tl_red": QColor(192, 57, 43),
    "tl_off": QColor(150, 150, 150),
    "heatmap_low": QColor(46, 204, 113, 50),
    "heatmap_med": QColor(241, 196, 15, 70),
    "heatmap_high": QColor(231, 76, 60, 90),
    "background": QColor(245, 245, 240),
    "grid": QColor(230, 230, 225),
    "junction": QColor(200, 200, 210),
    "junction_pen": QColor(180, 180, 190),
}


class MapViewer(QGraphicsView):
    COLORS = DARK_COLORS

    def __init__(self):
        super().__init__()
        self.scene_obj = QGraphicsScene()
        self.setScene(self.scene_obj)
        self.setRenderHints(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QBrush(self.COLORS["background"]))
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate
        )

        self.network_items = {}
        self.vehicle_items = {}
        self.tl_items = {}
        self.heatmap_items = {}
        self.show_heatmap = False
        self.show_vehicle_labels = False
        self.sim_controller = None
        self._scale = 1.0
        self._offset = QPointF(0, 0)
        self._current_net_path = ""
        self._road_labels: list[QGraphicsItem] = []
        self._vehicle_label_items: dict[str, QGraphicsItem] = {}

        # Tile background
        self._tile_provider = TileProvider()
        self._tile_style = "off"
        self._tile_items: dict[str, QGraphicsItem] = {}
        self._tile_zoom = 16
        self._conv_min = (0.0, 0.0)
        self._conv_max = (1000.0, 1000.0)
        self._orig_min = (0.0, 0.0)
        self._orig_max = (0.0, 0.0)

        # Vehicle trails & headlights
        self.show_trails = True
        self.show_headlights = True
        self._trail_history: dict[str, deque[tuple[float, float]]] = {}
        self._trail_items: dict[str, list[QGraphicsItem]] = {}
        self._headlight_items: dict[str, QGraphicsItem] = {}
        self._TRAIL_LENGTH = 10

        # Building footprints
        self._building_items: list[QGraphicsItem] = []

        # Traffic light lazy init — keyed by tlLogic ID (not junction ID)
        self._tl_init_done = False
        self._tl_junction_positions: dict[str, tuple[float, float]] = {}

        # Adaptive FPS
        self._target_fps = 30

        # Attribution label
        self._attribution = QLabel("", self)
        self._attribution.setStyleSheet(
            "color: rgba(0,0,0,150); background: rgba(255,255,255,180);"
            " padding: 2px 6px; font-size: 10px;"
        )
        self._attribution.move(6, self.height() - 22)
        self._attribution.setVisible(False)

        self._timer = QTimer()
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._update_view)
        self._timer.start()

    def set_sim_controller(self, controller):
        self.sim_controller = controller

    def load_network(self, net_path: str):
        import xml.etree.ElementTree as ET
        self._current_net_path = net_path
        self.scene_obj.clear()
        self.network_items.clear()
        self.vehicle_items.clear()
        self.tl_items.clear()
        self._trail_history.clear()
        self._trail_items.clear()
        self._headlight_items.clear()
        self._vehicle_label_items.clear()
        self._road_labels.clear()
        self._building_items.clear()
        self._clear_tiles()
        self._tl_init_done = False
        self._tl_junction_positions.clear()

        try:
            tree = ET.parse(net_path)
            root = tree.getroot()

            # Parse boundary for tile background
            loc = root.find("location")
            if loc is not None:
                cb = loc.get("convBoundary", "")
                ob = loc.get("origBoundary", "")
                if cb and ob:
                    parts = [float(v) for v in cb.split(",")]
                    self._conv_min = (parts[0], parts[1])
                    self._conv_max = (parts[2], parts[3])
                    parts = [float(v) for v in ob.split(",")]
                    self._orig_min = (parts[0], parts[1])
                    self._orig_max = (parts[2], parts[3])

            min_x = min_y = float("inf")
            max_x = max_y = float("-inf")

            # Draw edges (roads)
            pen_road = QPen(self.COLORS["road"], 2)
            for edge in root.findall(".//edge"):
                lane = edge.find("lane")
                if lane is not None:
                    shape_str = lane.get("shape", "")
                    if shape_str:
                        points = []
                        for coord in shape_str.split():
                            x_str, y_str, *_ = coord.split(",")
                            x, y = float(x_str), float(y_str)
                            points.append(QPointF(x, y))
                            min_x, min_y = min(min_x, x), min(min_y, y)
                            max_x, max_y = max(max_x, x), max(max_y, y)
                        if len(points) >= 2:
                            for i in range(len(points) - 1):
                                line = self.scene_obj.addLine(
                                    points[i].x(), points[i].y(),
                                    points[i+1].x(), points[i+1].y(),
                                    pen_road
                                )
                                self.network_items[edge.get("id", "")] = line

            # Draw junctions (intersections)
            pen_junction = QPen(self.COLORS["junction_pen"], 1)
            brush_junction = QBrush(self.COLORS["junction"])
            for junction in root.findall(".//junction"):
                x = float(junction.get("x", 0))
                y = float(junction.get("y", 0))
                jtype = junction.get("type", "")
                rect = self.scene_obj.addEllipse(
                    x - 3, y - 3, 6, 6, pen_junction, brush_junction
                )
                self.network_items[junction.get("id", "")] = rect

                # Store traffic light junction positions (TL items created lazily)
                if junction.get("tl") == "true" or "traffic_light" in jtype:
                    self._tl_junction_positions[junction.get("id")] = (x, y)

            # Road labels
            font_road = QFont("", 7)
            for edge in root.findall(".//edge"):
                name = edge.get("name", "")
                if name:
                    lane = edge.find("lane")
                    if lane is not None:
                        shape_str = lane.get("shape", "")
                        if shape_str:
                            coords = shape_str.split()
                            mid = len(coords) // 2
                            mx_str, my_str, *_ = coords[mid].split(",")
                            mx, my = float(mx_str), float(my_str)
                            label = self.scene_obj.addText(name, font_road)
                            label.setPos(QPointF(mx, my - 2))
                            label.setDefaultTextColor(self.COLORS["road"])
                            label.setZValue(-1)
                            self._road_labels.append(label)

            # Building footprints
            self._load_buildings(net_path)

            # Center view
            if min_x != float("inf"):
                cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2
                width, height = max_x - min_x, max_y - min_y
                self.scene_obj.setSceneRect(
                    min_x - 50, min_y - 50,
                    width + 100, height + 100
                )
                self.centerOn(QPointF(cx, cy))
                self._offset = QPointF(cx, cy)

            # Load tiles if style is active
            if self._tile_style != "off":
                self._render_tiles()

        except ET.ParseError as e:
            self.scene_obj.addText(f"Parse error: {e}")

    def set_tile_style(self, style: str) -> None:
        self._tile_style = style
        if style == "off":
            self._clear_tiles()
            self._attribution.setVisible(False)
        else:
            self._render_tiles()
            attr = self._tile_provider.get_attribution(style)
            self._attribution.setText(attr)
            self._attribution.setVisible(True)

    def _safe_remove_item(self, item):
        try:
            if item is not None and item.scene() is self.scene_obj:
                self.scene_obj.removeItem(item)
        except RuntimeError:
            pass

    def _clear_tiles(self) -> None:
        for item in self._tile_items.values():
            self._safe_remove_item(item)
        self._tile_items.clear()

    def _render_tiles(self) -> None:
        self._clear_tiles()
        if self._tile_style == "off":
            return
        if self._orig_min == self._orig_max:
            return

        lon_span = self._orig_max[0] - self._orig_min[0]
        lat_span = self._orig_max[1] - self._orig_min[1]
        if lon_span <= 0 or lat_span <= 0:
            return

        zoom = TileProvider.pick_zoom(lon_span, lat_span, target_tiles=8)
        self._tile_zoom = zoom

        # Determine bounding tile coordinates
        x_min, y_min = TileProvider.lonlat_to_tilexy(
            self._orig_min[0], self._orig_max[1], zoom,
        )
        x_max, y_max = TileProvider.lonlat_to_tilexy(
            self._orig_max[0], self._orig_min[1], zoom,
        )

        for tx in range(x_min, x_max + 1):
            for ty in range(y_min, y_max + 1):
                key = f"{zoom}/{tx}/{ty}"
                pix = self._tile_provider.get_tile(tx, ty, zoom, self._tile_style)
                if pix is None:
                    continue

                # Convert tile bounds (lat/lon) → SUMO xy
                lon0, lat0, lon1, lat1 = TileProvider.tilexy_to_bounds(tx, ty, zoom)
                sx0, sy0 = TileProvider.latlon_to_sumo(
                    lon0, lat0,
                    self._conv_min, self._conv_max,
                    self._orig_min, self._orig_max,
                )
                sx1, sy1 = TileProvider.latlon_to_sumo(
                    lon1, lat1,
                    self._conv_min, self._conv_max,
                    self._orig_min, self._orig_max,
                )

                w = abs(sx1 - sx0)
                h = abs(sy1 - sy0)
                item = self.scene_obj.addPixmap(pix)
                item.setPos(QPointF(min(sx0, sx1), min(sy0, sy1)))
                item.setTransformOriginPoint(QPointF(0, 0))
                item.setScale(1.0)
                # Scale pixmap to fit SUMO coordinate space
                if pix.width() > 0:
                    sx = w / pix.width()
                    sy = h / pix.height()
                    item.setScale(max(sx, sy))
                item.setZValue(-10)
                self._tile_items[key] = item

    def apply_theme(self, theme_name: str) -> None:
        if theme_name == "light":
            self.COLORS.update(LIGHT_COLORS)
        else:
            self.COLORS.update(DARK_COLORS)
        self.setBackgroundBrush(QBrush(self.COLORS["background"]))
        if self._current_net_path:
            self.load_network(self._current_net_path)

    def set_show_vehicle_labels(self, enabled: bool) -> None:
        self.show_vehicle_labels = enabled
        for item in self._vehicle_label_items.values():
            item.setVisible(enabled)

    def set_show_trails(self, enabled: bool) -> None:
        self.show_trails = enabled
        if not enabled:
            for items in self._trail_items.values():
                for item in items:
                    item.setVisible(False)

    def set_show_headlights(self, enabled: bool) -> None:
        self.show_headlights = enabled
        if not enabled:
            for item in self._headlight_items.values():
                item.setVisible(False)

    def _load_buildings(self, net_path: str) -> None:
        import json
        from pathlib import Path
        bld_path = Path(net_path).parent / "buildings.json"
        if not bld_path.exists():
            return
        try:
            data = json.loads(bld_path.read_text())
        except Exception:
            return
        building_brush = QBrush(QColor(160, 150, 140, 80))
        for bld in data:
            corners = bld.get("corners", [])
            if len(corners) < 3:
                continue
            try:
                pts = [QPointF(c[0], c[1]) for c in corners]
                poly = self.scene_obj.addPolygon(
                    QPolygonF(pts), QPen(Qt.PenStyle.NoPen), building_brush,
                )
                poly.setZValue(-8)
                self._building_items.append(poly)
            except Exception:
                pass

    def _update_view(self):
        t0 = time.perf_counter()

        if not self.sim_controller or not self.sim_controller.is_running:
            return

        tc = self.sim_controller.traci
        if not tc or not tc.is_connected:
            return

        try:
            tc = self.sim_controller.traci
            vehicles = tc.get_all_vehicles_cached()
            if not vehicles:
                vehicles = tc.get_all_vehicles()
            visible = set()

            for v in vehicles:
                vid = v.id
                visible.add(vid)
                angle_rad = math.radians(v.angle)

                color_map = {
                    "car": self.COLORS["vehicle_car"],
                    "truck": self.COLORS["vehicle_truck"],
                    "bus": self.COLORS["vehicle_bus"],
                    "emergency": self.COLORS["vehicle_emergency"],
                }
                color = color_map.get(v.vehicle_type, self.COLORS["vehicle_car"])

                # Main vehicle rect
                if vid in self.vehicle_items:
                    item = self.vehicle_items[vid]
                    item.setPos(QPointF(v.x, v.y))
                    item.setRotation(90 - v.angle)
                else:
                    rect = self.scene_obj.addRect(
                        -2, -1, 4, 2, QPen(Qt.PenStyle.NoPen), QBrush(color)
                    )
                    rect.setPos(QPointF(v.x, v.y))
                    rect.setRotation(90 - v.angle)
                    rect.setZValue(10)
                    self.vehicle_items[vid] = rect

                # ── Trails ──────────────────────────────────────
                if self.show_trails:
                    if vid not in self._trail_history:
                        self._trail_history[vid] = deque(maxlen=self._TRAIL_LENGTH)
                    self._trail_history[vid].append((v.x, v.y))

                    if vid not in self._trail_items:
                        items = []
                        for _ in range(self._TRAIL_LENGTH - 1):
                            dot = self.scene_obj.addEllipse(
                                -1, -1, 2, 2,
                                QPen(Qt.PenStyle.NoPen),
                                QBrush(QColor(255, 255, 255, 30)),
                            )
                            dot.setZValue(9)
                            dot.setVisible(False)
                            items.append(dot)
                        self._trail_items[vid] = items
                    else:
                        items = self._trail_items[vid]

                    history = list(self._trail_history[vid])
                    for i in range(len(items)):
                        idx = len(history) - 2 - i
                        if idx >= 0 and idx < len(history):
                            tx, ty = history[idx]
                            items[i].setPos(tx, ty)
                            alpha = max(25, 180 - i * 20)
                            items[i].setBrush(QBrush(QColor(255, 255, 255, alpha)))
                            items[i].setVisible(True)
                        else:
                            items[i].setVisible(False)

                # ── Vehicle Labels ──────────────────────────────
                if self.show_vehicle_labels and self._scale > 1.5:
                    speed_text = f"{v.speed:.1f}"
                    if vid in self._vehicle_label_items:
                        lbl = self._vehicle_label_items[vid]
                        lbl.setPos(QPointF(v.x - 5, v.y - 8))
                        lbl.setPlainText(speed_text)
                    else:
                        lbl = self.scene_obj.addText(
                            speed_text,
                            QFont("", 6),
                        )
                        lbl.setPos(QPointF(v.x - 5, v.y - 8))
                        lbl.setDefaultTextColor(QColor(255, 255, 255, 180))
                        lbl.setZValue(12)
                        self._vehicle_label_items[vid] = lbl
                elif vid in self._vehicle_label_items:
                    self._vehicle_label_items[vid].setVisible(False)

                # ── Headlights ──────────────────────────────────
                if self.show_headlights:
                    hx = v.x + math.cos(angle_rad) * 3.5
                    hy = v.y + math.sin(angle_rad) * 3.5
                    if vid in self._headlight_items:
                        hl = self._headlight_items[vid]
                        hl.setPos(QPointF(hx, hy))
                    else:
                        hl = self.scene_obj.addEllipse(
                            -1.2, -1.2, 2.4, 2.4,
                            QPen(Qt.PenStyle.NoPen),
                            QBrush(QColor(255, 255, 220, 120)),
                        )
                        hl.setPos(QPointF(hx, hy))
                        hl.setZValue(11)
                        self._headlight_items[vid] = hl

            # Cleanup vehicles that left
            for vid in list(self.vehicle_items.keys()):
                if vid not in visible:
                    self._safe_remove_item(self.vehicle_items.pop(vid))
                    if vid in self._trail_history:
                        del self._trail_history[vid]
                    if vid in self._trail_items:
                        for item in self._trail_items.pop(vid):
                            self._safe_remove_item(item)
                    if vid in self._headlight_items:
                        self._safe_remove_item(self._headlight_items.pop(vid))
                    if vid in self._vehicle_label_items:
                        self._safe_remove_item(self._vehicle_label_items.pop(vid))

            # ── Heatmap (weighted by speed) ─────────────────────
            if self.show_heatmap:
                self._render_heatmap(tc)

            # Lazy init TL items: map tlLogic ID → junction position via TraCI
            tl_ids = tc.get_tl_ids()
            if not self._tl_init_done:
                logger.info(f"TL lazy init: {len(tl_ids)} tl_ids, {len(self._tl_junction_positions)} junc positions")
                created = 0
                for tid in tl_ids:
                    try:
                        jid = tc.get_tl_junction_id(tid)
                        if jid in self._tl_junction_positions:
                            x, y = self._tl_junction_positions[jid]
                            self._create_tl_item(tid, x, y)
                            created += 1
                        else:
                            logger.warning(f"TL {tid}: jid {jid} NOT in _tl_junction_positions")
                    except Exception as e:
                        logger.warning(f"TL lazy init error for {tid}: {e}")
                        continue
                logger.info(f"TL lazy init done: created {created}/{len(tl_ids)} items")
                self._tl_init_done = True

            # Re-read tl_ids after init (items now exist with matching keys)
            tl_ids = tc.get_tl_ids()
            for tid in tl_ids:
                state = tc.get_cached_tl_state(tid)
                if state:
                    if 'y' in state:
                        ch = 'y'
                    elif 'g' in state:
                        ch = 'g'
                    elif 'r' in state or 'R' in state:
                        ch = 'r'
                    else:
                        ch = 'r'
                    self._update_tl(tid, ch)

        except Exception:
            pass

        # Adaptive FPS
        elapsed = time.perf_counter() - t0
        target = 1.0 / self._target_fps
        if elapsed > 1.5 * target and self._target_fps > 8:
            self._target_fps -= 2
        elif elapsed < 0.5 * target and self._target_fps < 30:
            self._target_fps += 1
        self._timer.setInterval(int(1000 / self._target_fps))

    def set_show_heatmap(self, enabled: bool):
        self.show_heatmap = enabled
        for item in self.heatmap_items.values():
            item.setVisible(enabled)

    def _render_heatmap(self, tc) -> None:
        for item in self.heatmap_items.values():
            item.setVisible(False)
        if not self.network_items:
            return
        for edge_id, line in self.network_items.items():
            if not isinstance(line, QGraphicsLineItem):
                continue
            data = tc.get_edge_data_cached(edge_id)
            if data is None:
                continue
            vcount = data.get("vehicle_count", 0)
            mspeed = data.get("mean_speed", 13.9)
            max_speed = 13.9
            congestion = vcount * max(0, 1.0 - mspeed / max_speed)
            if congestion > 0 and edge_id in self.network_items:
                if congestion < 2:
                    color = self.COLORS["heatmap_low"]
                elif congestion < 8:
                    color = self.COLORS["heatmap_med"]
                else:
                    color = self.COLORS["heatmap_high"]
                if edge_id not in self.heatmap_items:
                    item = self.scene_obj.addLine(
                        line.line().x1(), line.line().y1(),
                        line.line().x2(), line.line().y2(),
                        QPen(color, 3),
                    )
                    item.setZValue(5)
                    self.heatmap_items[edge_id] = item
                else:
                    item = self.heatmap_items[edge_id]
                item.setVisible(True)
                item.setPen(QPen(color, 3))

    def _create_tl_item(self, jid, x, y):
        r = 3
        gap = 2
        group = []
        colors = [
            QColor(231, 76, 60),    # red
            QColor(241, 196, 15),   # yellow
            QColor(46, 204, 113),   # green
        ]
        for i, c in enumerate(colors):
            off = QColor(60, 60, 60)
            circle = self.scene_obj.addEllipse(
                x - r, y - r + (i - 1) * (2 * r + gap),
                r * 2, r * 2,
                QPen(Qt.PenStyle.NoPen),
                QBrush(off)
            )
            circle.setZValue(20)
            group.append(circle)
        label = self.scene_obj.addText("", QFont("", 5))
        label.setPos(x - 3, y - 12)
        label.setZValue(20)
        group.append(label)
        self.tl_items[jid] = group

    def _update_tl(self, jid, state_char):
        group = self.tl_items.get(jid)
        if not group or len(group) < 3:
            return
        off = QColor(60, 60, 60)
        on_red = QColor(231, 76, 60)
        on_yellow = QColor(241, 196, 15)
        on_green = QColor(46, 204, 113)
        dim_red = QColor(180, 40, 30)

        # SUMO state chars: r=red, R=red+stop, y=yellow, Y=yellow+stop,
        # g=green, G=green+priority, u=red+yellow, O=off+blink, o=off
        red_on = state_char in ("r", "R", "u")
        yellow_on = state_char in ("y", "Y", "u")
        green_on = state_char in ("g", "G")

        group[0].setBrush(QBrush(on_red if red_on else off))      # red
        group[1].setBrush(QBrush(on_yellow if yellow_on else off)) # yellow
        group[2].setBrush(QBrush(on_green if green_on else off))   # green

    def clear_network(self):
        self.scene_obj.clear()
        self.network_items.clear()
        self.vehicle_items.clear()
        self.tl_items.clear()
        self._tl_init_done = False
        self._tl_junction_positions.clear()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._attribution.move(6, self.height() - 22)

    def wheelEvent(self, event):
        factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(factor, factor)
            self._scale *= factor
        else:
            self.scale(1 / factor, 1 / factor)
            self._scale /= factor
