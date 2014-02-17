VIRTUALENV=virtualenv
VENV=venv
PYTHON=$(VENV)/bin/python
DEV_STAMP=.dev_env_installed.stamp
INSTALL_STAMP=.install.stamp

.IGNORE: clean
.PHONY: all install virtualenv tests

OBJECTS = bin/ lib/ local/ include/ man/ pants.egg-info

all: install
install: $(INSTALL_STAMP)
$(INSTALL_STAMP): $(PYTHON)
	$(VENV)/bin/pip install -r requirements.txt
	$(PYTHON) setup.py develop
	touch $(INSTALL_STAMP)

install-dev: $(DEV_STAMP)
$(DEV_STAMP): $(PYTHON)
	$(VENV)/bin/pip install -r dev-requirements.txt
	touch $(DEV_STAMP)

virtualenv: $(PYTHON)
$(PYTHON):
	$(VIRTUALENV) $(VENV)

clean:
	rm -fr $(OBJECTS) $(DEV_STAMP) $(INSTALL_STAMP)

tests: install-dev
	$(VENV)/bin/nosetests --with-coverage --cover-package=pants -x -s

runserver: install
	$(VENV)/bin/pserve development.ini --reload
