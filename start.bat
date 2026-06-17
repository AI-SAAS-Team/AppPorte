@echo off
REM ============================================================
REM  AppDePorte - lance backend + frontend + tunnel public
REM  Double-clique sur ce fichier. 3 fenetres s'ouvrent.
REM  L'URL publique s'affiche dans la fenetre "TUNNEL".
REM ============================================================

set ROOT=%~dp0
set CF="C:\Program Files (x86)\cloudflared\cloudflared.exe"

echo Demarrage du backend (port 8000)...
start "BACKEND" cmd /k "cd /d %ROOT%backend && .venv\Scripts\python.exe -m uvicorn main:app --port 8000 --reload"

echo Demarrage du frontend (port 3000)...
start "FRONTEND" cmd /k "cd /d %ROOT%frontend && npx next start -p 3000"

echo Attente du demarrage des serveurs (12s)...
timeout /t 12 /nobreak >nul

echo Demarrage du tunnel public...
start "TUNNEL" cmd /k %CF% tunnel --url http://localhost:3000 --no-autoupdate

echo.
echo ============================================================
echo  Tout est lance. Regarde la fenetre "TUNNEL" : l'adresse
echo  https://xxxxx.trycloudflare.com est ton lien (change a
echo  chaque lancement). Ouvre-le sur ton telephone.
echo ============================================================
echo.
pause
