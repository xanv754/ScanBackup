COMPOSE := docker compose
LAYER ?= all
CMD ?= --help
DATA_DIRS := DataBackup/data SourceScrapper/data

.DEFAULT_GOAL := help

.PHONY: dirs up build down stop start restart clean fclean re logs ps scrape databackup mongo-shell help

# Crea los directorios montados como volumen con el usuario actual; si no existen,
# Docker los crea como root y los contenedores (no root) no pueden escribir en ellos.
dirs:
	@mkdir -p $(DATA_DIRS)

up: dirs
	$(COMPOSE) up -d

build: dirs
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

stop:
	$(COMPOSE) stop

start:
	$(COMPOSE) start

restart: down up

clean: down
	$(COMPOSE) down -v

fclean: clean
	-docker image rm -f scanbackup-databackup scanbackup-sourcescrapper

re: fclean build

logs:
	$(COMPOSE) logs -f $(SERVICE)

ps:
	$(COMPOSE) ps

scrape: dirs
	$(COMPOSE) run --rm sourcescrapper run --layer $(LAYER)

databackup: dirs
	$(COMPOSE) run --rm databackup $(CMD)

mongo-shell:
	docker exec -it scanbackup-mongodb sh -c 'mongosh -u "$$MONGO_APP_USER" -p "$$MONGO_APP_PASSWORD" --authenticationDatabase "$$MONGO_APP_DB" "$$MONGO_APP_DB"'

help:
	@echo "Reglas disponibles: up, build, down, stop, start, restart, clean, fclean, re, logs, ps, scrape, databackup, mongo-shell"
	@echo "Detalle de cada una en el README.md"
