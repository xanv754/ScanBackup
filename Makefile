HOMEPROJECT := $(shell echo "$$HOMEPROJECT")
VENV_EXISTS := $(shell if [ -d "$(HOMEPROJECT)/.venv" ]; then echo 1; else echo 0; fi)

.PHONY: venv setup

venv:
ifeq ($(VENV_EXISTS),0)
	@echo "Creando entorno virtual del sistema..."
	python -m venv $(HOMEPROJECT)/.venv
	$(HOMEPROJECT)/.venv/bin/pip install -r $(HOMEPROJECT)/requirements.txt
endif

setup: venv
	@echo "Creando directorios requeridos..."
	mkdir -p $(HOMEPROJECT)/data/SCAN/Borde
	mkdir -p $(HOMEPROJECT)/data/SCAN/Bras
	mkdir -p $(HOMEPROJECT)/data/SCAN/Caching
	mkdir -p $(HOMEPROJECT)/data/SCAN/RAI
	mkdir -p $(HOMEPROJECT)/data/SCAN/Reportes-Diarios
	mkdir -p $(HOMEPROJECT)/data/logs
	mkdir -p $(HOMEPROJECT)/routines/tmp/
	mkdir -p $(HOMEPROJECT)/sources/SCAN/
	touch $(HOMEPROJECT)/sources/SCAN/Borde.txt
	touch $(HOMEPROJECT)/sources/SCAN/Bras.txt
	touch $(HOMEPROJECT)/sources/SCAN/Caching.txt
	touch $(HOMEPROJECT)/sources/SCAN/RAI.txt
	@echo "Inicializando base de datos..."
	export PYTHONPATH=$(HOMEPROJECT)
	$(HOMEPROJECT)/.venv/bin/python -m database start
	@echo "Sistema instanciado correctamente."