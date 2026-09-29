@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
where py >nul 2>nul
if not errorlevel 1 goto use_launcher
where python >nul 2>nul
if not errorlevel 1 goto use_python
echo docs requires Python 3.11+ (or Python 3.10 with tomli). 1>&2
exit /b 127

:use_launcher
py -3 "%SCRIPT_DIR%md-book\docs.py" %*
exit /b %errorlevel%

:use_python
python "%SCRIPT_DIR%md-book\docs.py" %*
exit /b %errorlevel%
