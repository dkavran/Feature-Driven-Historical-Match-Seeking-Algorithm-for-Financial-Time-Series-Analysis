set venv=whiteshark

call %USERPROFILE%\Anaconda3\Scripts\activate %USERPROFILE%\Anaconda3
call activate %venv%

call conda env export --from-history | findstr -v "prefix" > ./config/environment.yml