# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path.cwd()
SRC = ROOT / "src"

hiddenimports = []
hiddenimports += collect_submodules("pydantic")
hiddenimports += collect_submodules("pydantic_core")
hiddenimports += ["yaml._yaml"]

datas = []
datas += collect_data_files("pydantic")
datas += collect_data_files("pydantic_core")
datas += collect_data_files("yaml")
datas += [(str(SRC / "rulebridge" / "web_assets"), "rulebridge/web_assets")]


a = Analysis(
    [str(SRC / "rulebridge_launcher.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "unittest", "tkinter"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="rulebridge",
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
)
