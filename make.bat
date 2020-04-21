@echo off
pyinstaller ^
  --onefile ^
  --noconsole ^
  --clean ^
  --noupx ^
  --win-private-assemblies ^
  --icon .\icone.ico ^
  --noconfirm ^
  fhotf.py
pause
rem   --noconsole ^
