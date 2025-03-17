set_env:
	pyenv virtualenv 3.10.6 rev2revenv
	pyenv local rev2revenv
	
upgrade_pip:
	python -m pip install --upgrade pip

install_requirements:
	@pip install -r requirements.txt

reinstall_package:
	@pip uninstall -y revpkg || :
	@pip install -e .

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -f */.ipynb_checkpoints
	@rm -Rf build
	@rm -Rf */__pycache__
	@rm -Rf */*.pyc

all: reinstall_package clean

run_api:
	cd api && uvicorn fast:app --reload
