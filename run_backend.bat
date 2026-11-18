@echo off
chcp 65001 > nul
echo ============================================================
echo  ContestMate 백엔드 서버를 시작합니다 (FastAPI on Port 8000)
echo ============================================================
cd /d "%~dp0backend"

:: 1. 기본 python 명령 시도
python -m uvicorn main:app --reload --port 8000
if %errorlevel% equ 0 goto end

:: 2. 기본 python 실패 시 사용자 전용 Python 경로로 재시도
echo.
echo [안내] 기본 python 경로를 찾을 수 없어 사용자 설치 경로로 실행합니다...
"C:\Users\jinwoo\AppData\Local\Python\bin\python.exe" -m uvicorn main:app --reload --port 8000

:end
pause
