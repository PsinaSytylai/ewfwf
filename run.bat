@echo off

if exist requirements.txt (
	echo installing wheel for faster installing
	pip install wheel
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found, skipping dependency installation.
)

echo Starting the bot...
python main.py

echo done
pause