set venv=whiteshark

call %USERPROFILE%\Anaconda3\Scripts\activate %USERPROFILE%\Anaconda3
call activate %venv%

call conda env update --file ./config/environment.yml --prune
call conda install --force-reinstall pip
call pip install -r ./config/requirements.txt