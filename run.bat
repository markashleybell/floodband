@echo off
call ..\scripts\activate.bat
echo Start server on port %HTTP_PLATFORM_PORT%
python __init__.py