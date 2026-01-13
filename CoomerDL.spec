# -*- mode: python ; coding: utf-8 -*-
"""
CoomerDL PyInstaller Specification File

This file configures PyInstaller to build a standalone executable for CoomerDL.
It includes all necessary dependencies, resources, and configurations for a
fully working Windows executable.

Usage:
    pyinstaller CoomerDL.spec
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all data files from resources directory
resources_datas = []
resources_dir = 'resources'
for root, dirs, files in os.walk(resources_dir):
    for file in files:
        file_path = os.path.join(root, file)
        dest_dir = os.path.dirname(file_path)
        resources_datas.append((file_path, dest_dir))

# Collect data files from dependencies
datas = resources_datas
datas += collect_data_files('customtkinter')
datas += collect_data_files('tkinterweb')
datas += collect_data_files('yt_dlp')
datas += collect_data_files('gallery_dl')

# Collect all submodules to ensure everything is included
hiddenimports = []
hiddenimports += collect_submodules('customtkinter')
hiddenimports += collect_submodules('tkinterweb')
hiddenimports += collect_submodules('yt_dlp')
hiddenimports += collect_submodules('gallery_dl')
hiddenimports += collect_submodules('cloudscraper')
hiddenimports += collect_submodules('selenium')
hiddenimports += collect_submodules('PIL')
hiddenimports += collect_submodules('bs4')
hiddenimports += collect_submodules('markdown2')

# Additional hidden imports for specific modules
hiddenimports += [
    'PIL._tkinter_finder',
    'pkg_resources.py2_warn',
    'urllib3',
    'requests',
    'psutil',
    'sqlite3',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'setuptools',
    ],
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
    name='CoomerDL',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app (no console window)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/img/window.ico',  # Application icon
    version_file=None,
)
