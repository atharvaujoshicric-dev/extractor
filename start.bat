@echo off
echo ============================================
echo   ContactMine - B2B Contact Intelligence
echo ============================================
echo.

echo [1/3] Installing Python dependencies...
cd backend
pip install -r requirements.txt -q
echo       Done!

echo [2/3] Starting Flask backend on port 5000...
start /B python app.py
timeout /t 2 /nobreak > nul
echo       Backend started!

echo [3/3] Opening frontend in browser...
cd ..
start "" "frontend\index.html"

echo.
echo ============================================
echo   ContactMine is running!
echo   Backend: http://localhost:5000
echo   Frontend: frontend/index.html
echo ============================================
echo.
pause
