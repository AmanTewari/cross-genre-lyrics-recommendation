@echo off

echo ======================================
echo LYRICS RECOMMENDATION PIPELINE START
echo ======================================

IF EXIST .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) ELSE IF EXIST venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

python main_pipeline.py

echo ======================================
echo PIPELINE COMPLETE
echo ======================================

pause
