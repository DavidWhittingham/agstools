@echo off

set scriptpath=%~dp0
set agsadminpath=..\agsadmin\Source
set arcpyextpath=..\arcpyext\Source
set buildtoolspath=..\buildtools

call:MakeAbsolute agsadminpath "%scriptpath%"
call:MakeAbsolute arcpyextpath "%scriptpath%"
call:MakeAbsolute buildtoolspath "%scriptpath%"

set PYTHONPATH=%agsadminpath%;%arcpyextpath%;%buildtoolspath%
echo PYTHONPATH set to: %PYTHONPATH%
echo.

cd /d Source\agstools

call cmd

GOTO:EOF

::----------------------------------------------------------------------------------
:: Function declarations
:: Handy to read http://www.dostips.com/DtTutoFunctions.php for how dos functions
:: work.
::----------------------------------------------------------------------------------
:MakeAbsolute file base -- makes a file name absolute considering a base path
::                      -- file [in,out] - variable with file name to be converted, or file name itself for result in stdout
::                      -- base [in,opt] - base path, leave blank for current directory
:$created 20060101 :$changed 20080219 :$categories Path
:$source http://www.dostips.com
SETLOCAL ENABLEDELAYEDEXPANSION
set "src=%~1"
if defined %1 set "src=!%~1!"
set "bas=%~2"
if not defined bas set "bas=%cd%"
for /f "tokens=*" %%a in ("%bas%.\%src%") do set "src=%%~fa"
( ENDLOCAL & REM RETURN VALUES
    IF defined %1 (SET %~1=%src%) ELSE ECHO.%src%
)
EXIT /b