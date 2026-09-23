@echo off

cd /d "C:\Users\Mohammed yahya\AIML"

echo Starting JupyterLab...

start "" "C:\Users\Mohammed yahya\anaconda3\Scripts\jupyter-lab.exe" --notebook-dir="C:\Users\Mohammed yahya\AIML"

echo JupyterLab is running.
echo.
echo This window will automatically commit your work
echo when JupyterLab is closed.
echo.

:CHECK
timeout /t 5 /nobreak >nul

tasklist | findstr /I "jupyter-lab.exe" >nul

if not errorlevel 1 goto CHECK

echo.
echo JupyterLab closed!
echo Checking for changes...

git add .

git diff --cached --quiet

if errorlevel 1 (
    echo Changes found.
    git commit -m "AIML practice - %date%"
    git push origin main
    echo.
    echo ==============================
    echo GitHub updated successfully!
    echo ==============================
) else (
    echo No changes to commit.
)

pause