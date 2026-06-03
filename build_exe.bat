@echo off
REM Construit l'executable Windows dans dist\OpenRouterExplorer.exe
REM Double-cliquez sur ce fichier, ou lancez-le depuis un terminal.

echo Installation des dependances de build...
python -m pip install -r requirements.txt pyinstaller

echo.
echo Construction de l'executable...
python -m PyInstaller OpenRouterExplorer.spec --noconfirm

echo.
echo Termine. L'executable se trouve dans : dist\OpenRouterExplorer.exe
pause
