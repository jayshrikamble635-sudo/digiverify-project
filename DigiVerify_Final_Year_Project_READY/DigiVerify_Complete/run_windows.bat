@echo off
cd /d "%~dp0"
if not exist .venv312 py -3.12 -m venv .venv312
call .venv312\Scripts\activate
python -m pip install flask pillow pytesseract gunicorn pyzbar
echo.
echo Launching DigiVerify with Automatic QR Engine...
echo.
python app.py
pause
