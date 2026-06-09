"""
Map Viewer Widget

Renders road network, vehicles, and traffic lights using QGraphicsView.
Updates in real-time during simulation.
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtCore import Qt, QRectF, QTimer, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QFont

from app.utils.logger import get_logger


class MapViewer(QGraphicsView):
    COLORS = {
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
    }

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
        self.sim_controller = None
        self._scale = 1.0
        self._offset = QPointF(0, 0)

        self._timer = QTimer()
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._update_view)
        self._timer.start()

    def set_sim_controller(self, controller):
        self.sim_controller = controller

    def load_network(self, net_path: str):
        import xml.etree.ElementTree as ET
        self.scene_obj.clear()
        self.network_items.clear()
        self.vehicle_items.clear()
        self.tl_items.clear()

        try:
            tree = ET.parse(net_path)
            root = tree.getroot()

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
            pen_junction = QPen(QColor(100, 100, 130), 1)
            brush_junction = QBrush(QColor(80, 80, 110))
            for junction in root.findall(".//junction"):
                x = float(junction.get("x", 0))
                y = float(junction.get("y", 0))
                jtype = junction.get("type", "")
                rect = self.scene_obj.addEllipse(
                    x - 3, y - 3, 6, 6, pen_junction, brush_junction
                )
                self.network_items[junction.get("id", "")] = rect

                # Traffic light indicator
                if junction.get("tl") == "true" or "traffic_light" in jtype:
                    tl_item = self.scene_obj.addEllipse(
                        x - 5, y - 5, 10, 10,
                        QPen(Qt.PenStyle.NoPen),
                        QBrush(self.COLORS["tl_red"])
                    )
                    self.tl_items[junction.get("id")] = tl_item

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

        except ET.ParseError as e:
            self.scene_obj.addText(f"Parse error: {e}")

    def _update_view(self):
        if not self.sim_controller or not self.sim_controller.is_running:
            return

        tc = self.sim_controller.traci
        if not tc or not tc.is_connected:
            return

        import traci
        try:
            veh_ids = traci.vehicle.getIDList()
            visible = set()

            for vid in veh_ids:
                try:
                    pos = traci.vehicle.getPosition(vid)
                    angle = traci.vehicle.getAngle(vid)
                    speed = traci.vehicle.getSpeed(vid)
                    veh_type = traci.vehicle.getTypeID(vid)
                except Exception:
                    continue

                color_map = {
                    "car": self.COLORS["vehicle_car"],
                    "truck": self.COLORS["vehicle_truck"],
                    "bus": self.COLORS["vehicle_bus"],
                    "emergency": self.COLORS["vehicle_emergency"],
                }
                color = color_map.get(veh_type, self.COLORS["vehicle_car"])
                visible.add(vid)

                if vid in self.vehicle_items:
                    item = self.vehicle_items[vid]
                    item.setPos(QPointF(pos[0], pos[1]))
                    item.setRotation(90 - angle)
                else:
                    rect = self.scene_obj.addRect(
                        -2, -1, 4, 2, QPen(Qt.PenStyle.NoPen), QBrush(color)
                    )
                    rect.setPos(QPointF(pos[0], pos[1]))
                    rect.setRotation(90 - angle)
                    rect.setZValue(10)
                    self.vehicle_items[vid] = rect

            # Remove vehicles that left
            for vid in list(self.vehicle_items.keys()):
                if vid not in visible:
                    self.scene_obj.removeItem(self.vehicle_items.pop(vid))

            # Update TL colors
            tl_ids = traci.trafficlight.getIDList()
            for tid in tl_ids:
                try:
                    phase = traci.trafficlight.getPhase(tid)
                    state = traci.trafficlight.getRedYellowGreenState(tid)
                except Exception:
                    continue
                color = self.COLORS["tl_red"]
                if state and len(state) > 0:
                    ch = state[0]
                    if ch == "G":
                        color = self.COLORS["tl_green"]
                    elif ch == "y":
                        color = self.COLORS["tl_yellow"]
                    elif ch == "r":
                        color = self.COLORS["tl_red"]
                for nid, item in self.tl_items.items():
                    item.setBrush(QBrush(color))

        except Exception:
            pass

    def set_show_heatmap(self, enabled: bool):
        self.show_heatmap = enabled
        for item in self.heatmap_items.values():
            item.setVisible(enabled)

    def clear_network(self):
        self.scene_obj.clear()
        self.network_items.clear()
        self.vehicle_items.clear()
        self.tl_items.clear()

    def wheelEvent(self, event):
        factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(factor, factor)
        else:
            self.scale(1 / factor, 1 / factor)
