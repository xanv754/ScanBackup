HOMEPROJECT := $(shell echo "$$HOMEPROJECT")
VENV_EXISTS := $(shell if [ -d "$(HOMEPROJECT)/.venv" ]; then echo 1; else echo 0; fi)

.PHONY: venv setup

venv:
ifeq ($(VENV_EXISTS),0)
	@echo "Creando entorno virtual del sistema..."
	python3 -m venv $(HOMEPROJECT)/.venv
	$(HOMEPROJECT)/.venv/bin/pip install .
endif

setup-files:
	@echo "Creando directorios requeridos..."
	mkdir -p $(HOMEPROJECT)/data/SCAN/BORDE
	mkdir -p $(HOMEPROJECT)/data/SCAN/BRAS
	mkdir -p $(HOMEPROJECT)/data/SCAN/CACHING
	mkdir -p $(HOMEPROJECT)/data/SCAN/RAI
	mkdir -p $(HOMEPROJECT)/data/SCAN/IXP
	mkdir -p $(HOMEPROJECT)/data/SCAN/IPBRAS
	mkdir -p $(HOMEPROJECT)/data/SCAN/DAILY_SUMMARY
	mkdir -p $(HOMEPROJECT)/data/logs
	mkdir -p $(HOMEPROJECT)/sources/SCAN/
	mkdir -p $(HOMEPROJECT)/sources/BK_SCAN/
	mkdir -p $(HOMEPROJECT)/scanbackup/routines/tmp/
	@echo "Creando archivos fuentes..."
	touch $(HOMEPROJECT)/sources/SCAN/BORDE
	touch $(HOMEPROJECT)/sources/SCAN/BRAS
	touch $(HOMEPROJECT)/sources/SCAN/CACHING
	touch $(HOMEPROJECT)/sources/SCAN/RAI
	touch $(HOMEPROJECT)/sources/SCAN/IXP
	touch $(HOMEPROJECT)/sources/SCAN/IPBRAS
	
setup: venv setup-folders setup-files
	@echo "Inicializando base de datos..."
	$(HOMEPROJECT)/.venv/bin/python -m scanbackup.database start
	@echo "Sistema instanciado correctamente."

run-scan:
	bash $(HOMEPROJECT)/scanbackup/routines/scanner.sh

run-daily:
	$(HOMEPROJECT)/.venv/bin/python -m scanbackup.routines.daily

run-updater:
	$(HOMEPROJECT)/.venv/bin/python -m scanbackup.updater data

run-updater-dev:
	$(HOMEPROJECT)/.venv/bin/python -m scanbackup.updater data --dev

run-base: run-scan run-daily

run: run-base run-updater

run-dev: run-base run-updater-dev

updater-sources:
	$(HOMEPROJECT)/.venv/bin/python -m scanbackup.updater sources

clean-data:
	@echo "Limpiando datos temporales..."
	rm -rf $(HOMEPROJECT)/data/SCAN/BORDE/*
	rm -rf $(HOMEPROJECT)/data/SCAN/BRAS/*
	rm -rf $(HOMEPROJECT)/data/SCAN/CACHING/*
	rm -rf $(HOMEPROJECT)/data/SCAN/RAI/*
	rm -rf $(HOMEPROJECT)/data/SCAN/IXP/*
	rm -rf $(HOMEPROJECT)/data/SCAN/IPBRAS/*
	rm -rf $(HOMEPROJECT)/data/SCAN/DAILY_SUMMARY/*
	rm -rf $(HOMEPROJECT)/scanbackup/routines/tmp/*