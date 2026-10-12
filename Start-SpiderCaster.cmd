@echo off
rem SpiderCaster cold-start launcher — double-click this file (click 1).
rem Finds Python, gates on doctor, builds the offline demo, opens the studio desk.
setlocal
set "SPIDERCASTER_HOME=%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%~dp0spidercaster.py" start %*
) else (
  python "%~dp0spidercaster.py" start %*
)
endlocal
