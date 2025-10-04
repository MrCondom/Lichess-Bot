@echo off
:loop
echo Starting Lichess Bot...
"C:\Users\JACKSON CHINEDU\AppData\Local\Microsoft\WindowsApps\python.exe" "C:\Users\JACKSON CHINEDU\lichess-bot\lichess-bot.py"
echo Bot stopped or crashed. Restarting in 30 seconds...
timeout /t 30 /nobreak
goto loop
