@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ============================================
echo   AdaWeldSystem LLM Wiki Browser
echo ============================================
echo.

REM ===== Step 1: 强制杀死所有旧的 wiki_server 进程 =====
echo [Step 1/3] 清理旧服务器进程...

REM 方式1: 通过窗口标题杀
taskkill /F /FI "WINDOWTITLE eq *wiki_server*" >nul 2>&1

REM 方式2: 通过 python 进程名杀（匹配 wiki_server.py）
for /f "tokens=2" %%p in ('wmic process where "name='python.exe' and commandline like '%%wiki_server%%'" get ProcessId /format:csv ^| findstr /r "[0-9]"') do (
    echo [INFO] Killing old python wiki_server (PID: %%p)
    taskkill /F /PID %%p >nul 2>&1
)

REM 方式3: 通过端口占用杀（最可靠）
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080.*LISTENING" 2^>nul') do (
    echo [INFO] Killing process occupying port 8080 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

REM 等待端口释放（最多等 3 秒）
echo [INFO] 等待端口 8080 释放...
for /l %%i in (1,1,6) do (
    netstat -ano | findstr ":8080.*LISTENING" >nul 2>&1
    if errorlevel 1 (
        echo [OK] Port 8080 is free
        goto :port_free
    )
    timeout /t 1 /nobreak >nul
)
echo [WARN] Port 8080 may still be in use, attempting to start anyway...

:port_free
timeout /t 1 /nobreak >nul

REM ===== Step 2: 启动服务器 =====
echo.
echo [Step 2/3] Starting wiki server...

where py >nul 2>&1
if %errorlevel%==0 (
    echo [INFO] Using py launcher
    py wiki_server.py
    goto :check_result
)

where python >nul 2>&1
if %errorlevel%==0 (
    echo [INFO] Using python
    python wiki_server.py
    goto :check_result
)

echo [ERROR] Python not found in PATH!
echo.
echo Please install Python from https://www.python.org/
echo or add Python to your PATH environment variable.
echo.
pause
exit /b 1

:check_result
if errorlevel 1 (
    echo.
    echo [ERROR] Server exited with error code %errorlevel%
    echo.
    pause
)
