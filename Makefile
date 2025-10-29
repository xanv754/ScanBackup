HOMEPROJECT := $(shell echo "$$HOMEPROJECT")
VENV_EXISTS := $(shell if [ -d "$(HOMEPROJECT)/.venv" ]; then echo 1; else echo 0; fi)

.PHONY: venv setup

venv:
ifeq ($(VENV_EXISTS),0)
	@echo "Creando entorno virtual del sistema..."
	python3 -m venv $(HOMEPROJECT)/.venv
	$(HOMEPROJECT)/.venv/bin/pip install .
endif

setup-folders:
	@echo "Creando directorios requeridos..."
	mkdir -p $(HOMEPROJECT)/data/SCAN/BORDE
	mkdir -p $(HOMEPROJECT)/data/SCAN/BRAS
	mkdir -p $(HOMEPROJECT)/data/SCAN/CACHING
	mkdir -p $(HOMEPROJECT)/data/SCAN/RAI
	mkdir -p $(HOMEPROJECT)/data/SCAN/IXP
	mkdir -p $(HOMEPROJECT)/data/SCAN/IP_BRAS
	mkdir -p $(HOMEPROJECT)/data/SCAN/DAILY_REPORT
	mkdir -p $(HOMEPROJECT)/data/logs
	mkdir -p $(HOMEPROJECT)/sources/SCAN/
	mkdir -p $(HOMEPROJECT)/sources/BK_SCAN/

setup-files:
	@echo "Creando archivos fuentes..."
	touch $(HOMEPROJECT)/sources/SCAN/BORDE
	touch $(HOMEPROJECT)/sources/SCAN/BRAS
	touch $(HOMEPROJECT)/sources/SCAN/CACHING
	touch $(HOMEPROJECT)/sources/SCAN/RAI
	touch $(HOMEPROJECT)/sources/SCAN/IXP
	touch $(HOMEPROJECT)/sources/SCAN/IP_BRAS

setup: venv setup-folders setup-files
	@echo "Inicializando base de datos..."
	$(HOMEPROJECT)/.venv/bin/python -m systemgrd.database start
	@echo "Sistema instanciado correctamente."

run-base:
	bash $(HOMEPROJECT)/systemgrd/routines/scan.sh
	$(HOMEPROJECT)/.venv/bin/python -m systemgrd.routines.daily

run: run-base
	$(HOMEPROJECT)/.venv/bin/python -m systemgrd.updater data

run-dev: run-base
	$(HOMEPROJECT)/.venv/bin/python -m systemgrd.updater data --dev

updater-sources:
	$(HOMEPROJECT)/.venv/bin/python -m systemgrd.updater sources

clean-data:
	@echo "Limpiando datos temporales..."
	rm -rf $(HOMEPROJECT)/data/SCAN/BORDE/*
	rm -rf $(HOMEPROJECT)/data/SCAN/BRAS/*
	rm -rf $(HOMEPROJECT)/data/SCAN/CACHING/*
	rm -rf $(HOMEPROJECT)/data/SCAN/RAI/*
	rm -rf $(HOMEPROJECT)/data/SCAN/IXP/*
	rm -rf $(HOMEPROJECT)/data/SCAN/IP_BRAS/*
	rm -rf $(HOMEPROJECT)/data/SCAN/DAILY_REPORT/*