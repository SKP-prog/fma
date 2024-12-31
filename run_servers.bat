cd %~dp0

@REM Start Web Server
call backend-app\run.bat
call frontend-app\run.bat
call crawler-app\run.bat

@REM Start Mongo Server
start /min cmd /k "mongod --dbpath C:\Users\shawn\OneDrive\Database\mongo-data"

