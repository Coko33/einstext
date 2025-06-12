# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
from PyInstaller.utils.hooks import collect_data_files

# Agregar rutas absolutas seguras
project_path = os.path.abspath('.')

datas = [
    ('fuentes', 'fuentes'),
    ('frames', 'frames'),
    ('modelos/vosk-model-small-es-0.42', 'modelos/vosk-model-small-es-0.42'),
    ('modelos/models--sentence-transformers--all-MiniLM-L6-v2', 'modelos/models--sentence-transformers--all-MiniLM-L6-v2'),
]

# Si preferís evitar hardcodear el path al .dll, podés detectar su ubicación automáticamente:
vosk_dll_path = os.path.join(project_path, 'venv', 'Lib', 'site-packages', 'vosk', 'libvosk.dll')
binaries = [(vosk_dll_path, 'vosk')]

a = Analysis(
    ['main.py'],
    pathex=[project_path],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=False,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Cambiar a True si querés consola
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
