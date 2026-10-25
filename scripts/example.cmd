@echo off
setlocal
if "%~1"=="" (echo Usage: example.cmd NAME & exit /b 2)
echo Hello %~1
