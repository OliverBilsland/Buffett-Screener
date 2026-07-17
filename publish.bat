@echo off
REM ============================================================
REM  Buffett Screener - one-click refresh + publish
REM  Runs the full-universe scan, writes index.html, pushes to GitHub.
REM  Double-click this file from inside the repo folder.
REM
REM  EDIT THE MARKET NUMBERS below when the market moves materially.
REM  They feed the Market Climate tab, so keep them roughly current.
REM ============================================================

set PY="C:\Users\obilsla\AppData\Local\Python\pythoncore-3.14-64\python.exe"

echo Running full-universe Buffett scan...
%PY% "buffett_screener_v15.py" --universe full --too-small-for-buffett ^
  --edgar-contact "bilsland@bc.edu" ^
  --market-forward-pe 22 --buffett-indicator-gnp 200 --treasury-10y 4.5 ^
  --publish --resume

if errorlevel 1 (
  echo.
  echo Screener failed - not publishing. Fix the error above and re-run.
  pause
  exit /b 1
)

echo.
echo Publishing to GitHub...
git add -A
git commit -m "Update dashboard %date% %time%"
git push

echo.
echo Done. Live in about a minute at your GitHub Pages URL.
pause
