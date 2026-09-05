@echo off
rem 启动 ST(SillyTavern)专用 facade,默认端口 8389(与网页端 8388 隔离)
cd /d %~dp0
..\python_embeded\python.exe -m uvicorn facade.st_main:app --host 0.0.0.0 --port 8389
pause
