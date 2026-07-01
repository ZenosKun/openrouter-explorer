#!/usr/bin/env bash
# Construit l'executable Linux/macOS dans dist/OpenRouterExplorer
# Usage : bash build_exe.sh
set -e

echo "Installation des dependances de build..."
python3 -m pip install -r requirements.txt pyinstaller

echo
echo "Construction de l'executable..."
python3 -m PyInstaller OpenRouterExplorer.spec --noconfirm

echo
echo "Termine. L'executable se trouve dans : dist/OpenRouterExplorer"
