@echo off
chcp 65001 >nul
title Compilador Portable EXE

cd /d "%~dp0"

set PYTHON_CMD=python
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)

echo [INFO] Comprobando PyInstaller...
%PYTHON_CMD% -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando PyInstaller...
    %PYTHON_CMD% -m pip install pyinstaller
)

echo [INFO] Compilando ejecutable standalone...
%PYTHON_CMD% -m PyInstaller --noconfirm --onedir --windowed ^
    --name "ExcelAnalyticsStudio" ^
    --add-data "assets;assets" ^
    --add-data "core;core" ^
    --add-data "ui;ui" ^
    app.py

if errorlevel 1 (
    echo [ERROR] Fallo la compilacion.
) else (
    echo [EXITO] Ejecutable generado en: dist\ExcelAnalyticsStudio\ExcelAnalyticsStudio.exe
)
pause
