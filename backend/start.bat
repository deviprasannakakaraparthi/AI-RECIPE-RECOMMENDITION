@echo off
SETLOCAL EnableDelayedExpansion

REM Get script directory
SET "SCRIPT_DIR=%~dp0"
CD /D "%SCRIPT_DIR%"

REM Set PYTHONPATH
SET "PYTHONPATH=%PYTHONPATH%;%cd%"

REM Check for .env file
IF NOT EXIST ".env" (
    echo GOOGLE_API_KEY=your_key_here > .env
    echo .env file created. Please add your Gemini API Key.
)

REM Check if venv exists
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
    CALL venv\Scripts\activate.bat
    echo Installing requirements...
    pip install -r requirements.txt
) ELSE (
    CALL venv\Scripts\activate.bat
)

REM Run the server
echo Starting server...
echo Access at http://localhost:8000
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

ENDLOCAL
