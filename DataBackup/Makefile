VENV = .venv
PYTHON = $(VENV)/bin/python

updater:
	$(PYTHON) -m scanbackup sources traffic-export --dirpath ./data/sources

test:
	$(PYTHON) -m unittest discover -s tests -t . -v
