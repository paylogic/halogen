# create virtual environment
.venv:
	python3 -m venv .venv

# install all needed for development
develop: .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e . -r requirements-testing.txt tox

# clean the development environment
clean:
	-rm -rf .venv
