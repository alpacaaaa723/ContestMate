@echo off
chcp 65001 > nul
echo ============================================================
echo  ContestMate 프론트엔드 서버를 시작합니다 (Vite on Port 5173)
echo ============================================================
cd /d "%~dp0frontend"
npm run dev
pause
