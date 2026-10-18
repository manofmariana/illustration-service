@echo off
rem Start illustration gateway: all modes on one port (default 8388)
cd /d %~dp0
..\python_embeded\python.exe -m uvicorn facade.gateway:app --host 0.0.0.0 --port 8388
pause
