@echo off
cd /d D:\PythonProject\CC_Agent\src\plan_and_execute_agent
echo Installing dependencies...
python -m pip install -r requirements.txt
echo.
echo Installation complete!
echo.
echo You can now run:
echo   python test_simple.py
echo   python main.py
pause