start /min cmd /k "cd %~dp0 & env\Scripts\activate.bat & env\Scripts\python.exe manage.py runserver"

start /min cmd /k "cd %~dp0 & env\Scripts\activate.bat & env\Scripts\python.exe manage.py crawl"