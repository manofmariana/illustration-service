@echo off
rem Start ST(SillyTavern) facade service, port 8389
cd /d %~dp0
..\python_embeded\python.exe -m uvicorn facade.st_main:app --host 0.0.0.0 --port 8389
pause
