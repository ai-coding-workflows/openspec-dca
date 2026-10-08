@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
if not defined BOOK_BUILDER set "BOOK_BUILDER=%SCRIPT_DIR%md-book-builder\book.py"
rem An activated venv supplies optional exporter dependencies (for example typst).
if defined VIRTUAL_ENV goto use_python
where py >nul 2>nul
if not errorlevel 1 goto use_launcher
where python >nul 2>nul
if not errorlevel 1 goto use_python
echo book requires Python 3.11+ (or Python 3.10 with tomli). 1>&2
exit /b 127

:use_launcher
py -3 "%BOOK_BUILDER%" %*
exit /b %errorlevel%

:use_python
python "%BOOK_BUILDER%" %*
exit /b %errorlevel%
