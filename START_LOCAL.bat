@echo off
echo ========================================
echo Starting Expense Tracker (Local Mode)
echo ========================================
echo.

echo Step 1: Setting up Backend...
cd backend

echo Creating virtual environment...
if not exist venv (
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing backend dependencies...
pip install -r requirements.txt

echo.
echo Step 2: Starting Backend API...
start cmd /k "cd /d %cd% && venv\Scripts\activate && echo Backend running on http://localhost:8000 && echo API Docs: http://localhost:8000/docs && uvicorn app.main_local:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5

echo.
echo Step 3: Setting up Frontend...
cd ..\frontend

echo Installing frontend dependencies...
call npm install

echo.
echo Step 4: Starting Frontend...
start cmd /k "cd /d %cd% && echo Frontend running on http://localhost:3000 && npm run dev"

echo.
echo ========================================
echo Application Starting!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo Wait 10 seconds, then open http://localhost:3000 in your browser
echo.
echo Press any key to open the browser automatically...
pause
start http://localhost:3000

echo.
echo To stop the application, close the terminal windows.
echo.
