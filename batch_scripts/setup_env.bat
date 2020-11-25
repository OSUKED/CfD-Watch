call cd ..
call conda env create -f environment.yml
call conda activate CfDWatch
call ipython kernel install --user --name=CfDWatch
pause