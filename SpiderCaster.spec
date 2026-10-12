# -*- mode: python ; coding: utf-8 -*-


# SpiderCaster portable spec: bundle engine data so the exe runs from any
# cold-machine folder (no absolute dev paths, no CWD dependence).
# Rebuild: pyinstaller SpiderCaster.spec (stdlib-only engine, no hidden imports)
import os

_here = os.path.dirname(os.path.abspath(SPEC)) if 'SPEC' in globals() else os.getcwd()

a = Analysis(
    [os.path.join(_here, 'spidercaster.py')],
    pathex=[_here],
    binaries=[],
    datas=[
        (os.path.join(_here, 'library'), 'library'),
        (os.path.join(_here, 'plugin'), 'plugin'),
        (os.path.join(_here, 'projects', 'demo-local'), os.path.join('projects', 'demo-local')),
        (os.path.join(_here, 'projects', 'bench-harbor-tearoom'),
         os.path.join('projects', 'bench-harbor-tearoom')),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='SpiderCaster',
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
