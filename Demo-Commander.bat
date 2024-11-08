@echo off
tasklist /FI "IMAGENAME eq steam.exe" | findstr /I steam.exe
if not errorlevel 1 (
    taskkill /F /IM steam.exe
    timeout /t 2 /nobreak
) else (
    echo Steam ist nicht gestartet, daher wird nichts beendet.
)
start "" "C:\Program Files (x86)\Steam\steam.exe" -login Demo-Name Demo-Passwort
timeout /t 5 /nobreak
start "" steam://rungameid/359320
exit
    