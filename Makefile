COMPOSE := docker compose
LAYER ?= all
CMD ?= --help

.DEFAULT_GOAL := help

.PHONY: up build down stop start restart clean fclean re logs ps scrape databackup mongo-shell help

up:
	$(COMPOSE) up -d

build:
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

scrape:
	$(COMPOSE) run --rm sourcescrapper run --layer $(LAYER)

databackup:
	$(COMPOSE) run --rm databackup $(CMD)

mongo-shell:
	docker exec -it scanbackup-mongodb sh -c 'mongosh -u "$$MONGO_APP_USER" -p "$$MONGO_APP_PASSWORD" --authenticationDatabase "$$MONGO_APP_DB" "$$MONGO_APP_DB"'

help:
	@echo "Reglas disponibles: up, build, down, stop, start, restart, clean, fclean, re, logs, ps, scrape, databackup, mongo-shell"
	@echo "Detalle de cada una en el README.md"
