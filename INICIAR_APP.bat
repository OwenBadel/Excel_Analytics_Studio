@echo off
chcp 65001 >nul
title Excel Analytics Studio

cd /d "%~dp0"

REM 1. Localizar interprete de Python
set PYTHON_CMD=
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)

if "%PYTHON_CMD%"=="" (
    where python >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" (
    where py >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=py -3"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] No se detecto ninguna instalacion de Python.
    echo Instale Python 3.10 o superior desde https://python.org
    pause
    exit /b 1
)

echo [OK] Python detectado correctamente.
echo [INFO] Iniciando Excel Analytics Studio...

REM 2. Comprobar librerias criticas
%PYTHON_CMD% -c "import PyQt5, PyQt5.QtWebEngineWidgets, pandas, openpyxl, xlsxwriter, plotly, matplotlib" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando librerias faltantes desde requirements.txt...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Fallo la instalacion de dependencias con pip.
        pause
        exit /b 1
    )
)

REM 3. Ejecutar la aplicacion principal
%PYTHON_CMD% app.py

if errorlevel 1 (
    echo.
    echo [AVISO] La aplicacion finalizo con codigo de error.
    pause
)
