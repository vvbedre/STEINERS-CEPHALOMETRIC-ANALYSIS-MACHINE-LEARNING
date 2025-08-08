@echo off
:: Check if a file is dragged onto the script
if "%~1"=="" (
    echo Drag and drop a Python file onto this batch file to run it.
    pause
    exit
)

:: Run the dragged file with Python
python "%~1"

:: Keep the window open to see any output
pause
