@echo off
setlocal enabledelayedexpansion

for /f "usebackq tokens=1,2 delims==" %%A in (".env") do (
    set "key=%%A"
    set "val=%%B"
    setx !key! "!val!" >nul
    echo !key! = !val!
)

echo.
echo Environment variables loaded. Restart your terminal/IDE to load them.
pause
