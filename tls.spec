# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for TLS - Traffic Light Simulation

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('sim', 'sim'),
        ('resources', 'resources'),
        ('README.md', '.'),
        ('PROJECT_STRUCTURE.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'traci',
        'traci._constants',
        'traci.constants',
        'traci.domain',
        'traci.edge',
        'traci.vehicle',
        'traci.trafficlight',
        'traci.simulation',
        'traci.lane',
        'traci.inductionloop',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        'pyqtgraph',
        'xml.etree.ElementTree',
        'xml.etree',
        'xml',
        'urllib.request',
        'urllib',
        'csv',
        'json',
        'sqlite3',
        'threading',
        'collections',
        'statistics',
        'math',
        'time',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'PIL',
        'cv2',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngine',
        'PyQt6.QtWebChannel',
        'notebook',
        'ipython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

icon_path = 'resources/icon.ico' if Path('resources/icon.ico').exists() else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='tls',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='TLS.app',
        icon=icon_path,
        bundle_identifier='com.tls.traffic-light-sim',
    )
