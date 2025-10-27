set new_venv=whiteshark

call conda clean --all
call conda env create -n %new_venv% --file ./config/environment.yml
call activate %new_venv%
call conda install --force-reinstall pip
call pip install -r ./config/requirements.txt
call conda install ipykernel nb_conda_kernels brotlipy
call python -m ipykernel install --user --name whiteshark --display-name "Python (whiteshark)"