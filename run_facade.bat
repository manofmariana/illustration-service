@echo off
cd /d %~dp0
set PYTHONPATH=%~dp0
set KIMITOKEN=o78uXOeipNGYJ13OXAMuy9IHDkuctwA0GgqrUhNgML0
..\python_embeded\python.exe -m uvicorn facade.main:app --host 0.0.0.0 --port 8388
