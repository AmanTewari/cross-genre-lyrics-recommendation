@echo off

echo ======================================
echo LYRICS RECOMMENDATION PIPELINE START
echo ======================================

IF EXIST .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) ELSE IF EXIST venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

set SKIP_STEPS=

call :prompt_skip "Step 1 - Preprocessing" run_step1.py
call :prompt_skip "Step 2 - Feature extraction" run_step2.py
call :prompt_skip "Step 3 - Clustering" run_step3.py
call :prompt_skip "Step 4 - Recommendation checks" run_step4.py

if defined SKIP_STEPS (
    echo Skipping: %SKIP_STEPS%
    python main_pipeline.py --skip %SKIP_STEPS%
) else (
    python main_pipeline.py
)

echo ======================================
echo PIPELINE COMPLETE
echo ======================================

pause

goto :eof

:prompt_skip
set USER_INPUT=
set /p USER_INPUT=%~1 ^(press Enter to run, type skip to skip^): 
if /I "%USER_INPUT%"=="skip" (
    if defined SKIP_STEPS (
        set SKIP_STEPS=%SKIP_STEPS% %~2
    ) else (
        set SKIP_STEPS=%~2
    )
)
exit /b
