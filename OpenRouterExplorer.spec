# -*- mode: python ; coding: utf-8 -*-
"""Recette de build PyInstaller, multiplateforme.

Embarque automatiquement les assets de CustomTkinter (thèmes + polices)
qui ne sont pas détectés tout seuls, ce qui fait planter l'exe sinon.

Usage :
    pyinstaller OpenRouterExplorer.spec
"""

import os
import customtkinter

# Dossier d'installation de customtkinter (contient assets/ et thèmes JSON)
ctk_path = os.path.dirname(customtkinter.__file__)

block_cipher = None

a = Analysis(
    ["run.py"],
    pathex=[],
    binaries=[],
    datas=[(ctk_path, "customtkinter")],
    hiddenimports=["customtkinter"],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="OpenRouterExplorer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # pas de fenêtre console : c'est une app graphique
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
