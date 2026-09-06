@echo off
rem Start web facade service, port 8388
cd /d %~dp0
..\python_embeded\python.exe -m uvicorn facade.main:app --host 0.0.0.0 --port 8388
pause
