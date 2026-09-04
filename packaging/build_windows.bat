@echo off
setlocal

cd /d "%~dp0.."

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
) else (
    where py >nul 2>&1
    if errorlevel 1 (
        set "PYTHON_CMD=python"
    ) else (
        set "PYTHON_CMD=py"
    )
)

if not exist "build" mkdir "build"

"%PYTHON_CMD%" -c "from PIL import Image; Image.open(r'%CD%\src\topos_power\assets\topos-power-icon.png').save(r'%CD%\build\topos-power.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"
if errorlevel 1 (
    echo Failed to create the Windows icon. Install Pillow first:
    echo %PYTHON_CMD% -m pip install pillow
    exit /b 1
)

"%PYTHON_CMD%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name "Topos Power" ^
    --paths src ^
    --icon "%CD%\build\topos-power.ico" ^
    --add-data "%CD%\src\topos_power\assets\topos-power-icon.png;topos_power/assets" ^
    --specpath "%CD%\build" ^
    --distpath "%CD%\dist" ^
    --workpath "%CD%\build\pyinstaller" ^
    "%CD%\packaging\app_entry.py"
if errorlevel 1 exit /b %errorlevel%

echo Built: %CD%\dist\Topos Power\Topos Power.exe
endlocal
