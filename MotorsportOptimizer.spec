# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

BASE_DIR = Path.cwd().resolve()

datas = [
    (str(BASE_DIR / "frontend" / "dist"), "frontend/dist"),
    (str(BASE_DIR / "data"), "data"),
]

hiddenimports = [
    "uvicorn",
    "uvicorn.config",
    "uvicorn.main",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespans",
    "uvicorn.lifespans.on",
    "uvicorn.lifespans.off",
    "uvicorn.lifespans.auto",
    "fastapi",
    "starlette",
    "starlette.staticfiles",
    "pydantic",
    "pydantic_settings",
    "sqlalchemy",
    "sqlalchemy.sql.default_comparator",
    "sqlite3",
    "numpy",
    "scipy",
    "scipy.stats",
    "scipy.optimize",
    "scipy.special",
    "webview",
    "webview.platforms.winforms",
    "clr",
    "pythonnet",
]

# Collect any additional submodules for app and uvicorn
hiddenimports += collect_submodules("app")
hiddenimports += collect_submodules("uvicorn")

a = Analysis(
    [str(BASE_DIR / "desktop_app.py")],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "IPython", "jupyter"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="MotorsportOptimizer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to True so console logs show backend status & user sees launch log
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
