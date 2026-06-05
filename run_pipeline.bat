@echo off
setlocal enabledelayedexpansion

REM Get the directory where this batch file is located (project root)
set PROJECT_ROOT=%~dp0

REM Change to project root
cd /d "%PROJECT_ROOT%"

echo ======================================
echo LYRICS RECOMMENDATION PIPELINE START
echo ======================================
echo Project root: %PROJECT_ROOT%
echo.

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
)

echo.

REM Initialize skip list
set SKIP_LIST=

REM Prompt for each step
call :prompt_step "Step 1 - Preprocessing" 1
call :prompt_step "Step 2 - Feature extraction" 2
call :prompt_step "Step 3 - Clustering" 3
call :prompt_step "Step 4 - Recommendation checks" 4
call :prompt_step "Step 5 - Validation" 5

REM Run pipeline with skips
if defined SKIP_LIST (
    echo.
    echo Running pipeline with skips: %SKIP_LIST%
    echo.
    python pipeline\main_pipeline.py --skip %SKIP_LIST%
) else (
    echo.
    echo Running full pipeline...
    echo.
    python pipeline\main_pipeline.py
)

if errorlevel 1 (
    echo.
    echo ERROR: Pipeline failed!
    echo.
) else (
    echo.
    echo SUCCESS: Pipeline completed!
    echo.
)

pause
exit /b

:prompt_step
set /p USER_INPUT=%~1 (press Enter to run, type 'skip' to skip): 
if /i "!USER_INPUT!"=="skip" (
    set SKIP_LIST=!SKIP_LIST! %~2
)
exit /b



i have an appointment with them today sir, and i need the following details:
Company Name:
Contact Person:
Contact Number:
Email Address:
and offer letter if possible.