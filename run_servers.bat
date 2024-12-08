cd %~dp0
call backend-app\run.bat
call frontend-app\run.bat

mongod --dbpath "C:\Users\shawn\OneDrive\Database\mongo-data"