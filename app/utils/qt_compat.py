try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    import PyQt5.QtCore
    import PyQt5.QtGui
    import PyQt5.QtWidgets

    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *

    Qt = PyQt5.QtCore.Qt

    QAction = PyQt5.QtWidgets.QAction

    Qt.Orientation = type('Orientation', (), {
        'Horizontal': Qt.Horizontal, 'Vertical': Qt.Vertical,
    })

    Qt.ScrollBarPolicy = type('ScrollBarPolicy', (), {
        'ScrollBarAlwaysOff': Qt.ScrollBarAlwaysOff,
        'ScrollBarAsNeeded': Qt.ScrollBarAsNeeded,
        'ScrollBarAlwaysOn': Qt.ScrollBarAlwaysOn,
    })

    Qt.PenStyle = type('PenStyle', (), {
        'NoPen': Qt.NoPen, 'SolidLine': Qt.SolidLine,
        'DashLine': Qt.DashLine, 'DotLine': Qt.DotLine,
    })

    QFont.Weight = type('Weight', (), {
        'Thin': QFont.Thin, 'Light': QFont.Light,
        'Normal': QFont.Normal, 'Bold': QFont.Bold,
        'Black': QFont.Black,
    })

    QPainter.RenderHint = type('RenderHint', (), {
        'Antialiasing': QPainter.Antialiasing,
        'TextAntialiasing': QPainter.TextAntialiasing,
        'SmoothPixmapTransform': QPainter.SmoothPixmapTransform,
    })

    QGraphicsView.DragMode = type('DragMode', (), {
        'NoDrag': QGraphicsView.NoDrag,
        'ScrollHandDrag': QGraphicsView.ScrollHandDrag,
        'RubberBandDrag': QGraphicsView.RubberBandDrag,
    })

    QGraphicsView.ViewportUpdateMode = type('ViewportUpdateMode', (), {
        'FullViewportUpdate': QGraphicsView.FullViewportUpdate,
        'MinimalViewportUpdate': QGraphicsView.MinimalViewportUpdate,
        'SmartViewportUpdate': QGraphicsView.SmartViewportUpdate,
        'NoViewportUpdate': QGraphicsView.NoViewportUpdate,
        'BoundingRectViewportUpdate': QGraphicsView.BoundingRectViewportUpdate,
    })
