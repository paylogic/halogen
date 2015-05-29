SHELL := /bin/bash
ifndef local_env
PATH := $(PWD)/.env/bin:$(PATH)
endif
PYTHON_VERSION := 2.7
pip := pip

# Prepare project for development
develop: env
	$(pip) install -e .[test] tox $(pip_args)

# Create environment for project
# - remove all files from .env/bin folder which starts with python
# - create virtual environment
# - create symling for cairo project
env:
ifndef local_env
	rm -rf .env/bin/python* .env/bin/virtualenv || echo
	virtualenv .env --python=python$(PYTHON_VERSION)
endif

# Run tests for package
test: develop
	tox

clean:
	-rm -rf ./build ./env
	-hg --config extensions.hgext.purge= purge --all

.PHONY: clean env
