# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['3DOBJ.py'],
    pathex=[],
    binaries=[],
    datas=[('resources\\pyramid.obj', 'resources'), ('resources\\sphere.obj', 'resources'), ('resources\\cube.obj', 'resources'), ('resources\\cube24.obj', 'resources')],
    hiddenimports=['pygame', 'OpenGL.GL', 'OpenGL.GLU', 'OpenGL', 'OpenGL.GLUT','PyOpenGL-accelerate'],
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
    name='3DOBJ',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
