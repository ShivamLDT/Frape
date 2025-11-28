@echo off
REM Installation script for Beam (Windows)

echo Installing Beam CLI...
echo ======================

REM Check Python version
python --version
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.10 or higher.
    exit /b 1
)

REM Install beam in development mode
echo.
echo Installing beam in development mode...
pip install -e .

REM Check if bench is installed
where bench >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo Bench is already installed
    bench --version
) else (
    echo.
    echo Installing frappe-bench as dependency...
    pip install frappe-bench
)

echo.
echo ======================
echo Installation complete!
echo.
echo Test beam with:
echo   beam --version
echo   beam --help
echo.
echo See TESTING.md for comprehensive testing instructions.

pause

