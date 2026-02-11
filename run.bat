@echo off
:main
echo Starting the Important Grrl...
python main.py
echo The Important Grrl has crashed. Attempting to restart in 1 minute...
timeout /t 60 /nobreak
goto:main
cmd /k 