PWDSCANBACKUP := $(shell echo "$$PWDSCANBACKUP")
VENV_EXISTS := $(shell if [ -d "$(PWDSCANBACKUP)/.venv" ]; then echo 1; else echo 0; fi)

.PHONY: venv setup

venv:
ifeq ($(VENV_EXISTS),0)
	@echo "Creando entorno virtual del sistema..."
	python3 -m venv $(PWDSCANBACKUP)/.venv
	$(PWDSCANBACKUP)/.venv/bin/pip install .
endif

setup-files:
	@echo "Creando directorios requeridos..."
	mkdir -p $(PWDSCANBACKUP)/data/SCAN/BORDE
	mkdir -p $(PWDSCANBACKUP)/data/SCAN/BRAS
	mkdir -p $(PWDSCANBACKUP)/data/SCAN/CACHING
	mkdir -p $(PWDSCANBACKUP)/data/SCAN/RAI
	mkdir -p $(PWDSCANBACKUP)/data/SCAN/IXP
	mkdir -p $(PWDSCANBACKUP)/data/SCAN/IPBRAS
	mkdir -p $(PWDSCANBACKUP)/data/SCAN/DAILY_SUMMARY
	mkdir -p $(PWDSCANBACKUP)/data/logs
	mkdir -p $(PWDSCANBACKUP)/sources/SCAN/
	mkdir -p $(PWDSCANBACKUP)/sources/BK_SCAN/
	mkdir -p $(PWDSCANBACKUP)/scanbackup/routines/tmp/
	@echo "Creando archivos fuentes..."
	touch $(PWDSCANBACKUP)/sources/SCAN/BORDE
	touch $(PWDSCANBACKUP)/sources/SCAN/BRAS
	touch $(PWDSCANBACKUP)/sources/SCAN/CACHING
	touch $(PWDSCANBACKUP)/sources/SCAN/RAI
	touch $(PWDSCANBACKUP)/sources/SCAN/IXP
	touch $(PWDSCANBACKUP)/sources/SCAN/IPBRAS
	
setup: venv setup-files
	@echo "Inicializando base de datos..."
	$(PWDSCANBACKUP)/.venv/bin/python -m scanbackup.database start
	@echo "Sistema instanciado correctamente."

run-scanner:
	bash $(PWDSCANBACKUP)/scanbackup/routines/scanner.sh

run-daily:
	$(PWDSCANBACKUP)/.venv/bin/python -m scanbackup.routines.daily

run-updater:
	$(PWDSCANBACKUP)/.venv/bin/python -m scanbackup.updater data

run-updater-dev:
	$(PWDSCANBACKUP)/.venv/bin/python -m scanbackup.updater data --dev

run-base: run-scanner run-daily

run: run-base run-updater

run-dev: run-base run-updater-dev

updater-sources:
	$(PWDSCANBACKUP)/.venv/bin/python -m scanbackup.updater sources

clean-data:
	@echo "Limpiando datos temporales..."
	rm -rf $(PWDSCANBACKUP)/data/SCAN/BORDE/*
	rm -rf $(PWDSCANBACKUP)/data/SCAN/BRAS/*
	rm -rf $(PWDSCANBACKUP)/data/SCAN/CACHING/*
	rm -rf $(PWDSCANBACKUP)/data/SCAN/RAI/*
	rm -rf $(PWDSCANBACKUP)/data/SCAN/IXP/*
	rm -rf $(PWDSCANBACKUP)/data/SCAN/IPBRAS/*
	rm -rf $(PWDSCANBACKUP)/data/SCAN/DAILY_SUMMARY/*
	rm -rf $(PWDSCANBACKUP)/scanbackup/routines/tmp/*