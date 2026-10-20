DEV_ENV_FILE ?= .env.development
PROD_ENV_FILE ?= .env.production
ARGS ?=

COMPOSE_DEV = docker compose --env-file $(DEV_ENV_FILE) -f docker-compose.dev.yml
COMPOSE_PROD = docker compose --env-file $(PROD_ENV_FILE) -f docker-compose.yml

SERVICES = interface-sync traffic-collector reports

.PHONY: init \
	dev-build dev-up dev-down dev-clean dev-logs \
	dev-sync dev-collect dev-report dev-test \
	dev-sim-up dev-sim-down dev-sim-restart dev-sim-status dev-sim-logs \
	prod-build prod-up prod-down prod-logs \
	prod-sync prod-collect prod-report

init:
	mkdir -p exports $(addprefix logs/,$(SERVICES))

dev-build:
	$(COMPOSE_DEV) --profile services build

dev-up:
	$(COMPOSE_DEV) up -d mongo

dev-down:
	$(COMPOSE_DEV) --profile services down

dev-clean:
	$(COMPOSE_DEV) --profile services down --volumes

dev-logs:
	$(COMPOSE_DEV) logs -f mongo

dev-sync:
	$(COMPOSE_DEV) run --rm interface-sync $(ARGS)

dev-collect:
	$(COMPOSE_DEV) run --rm traffic-collector $(ARGS)

dev-report:
	$(COMPOSE_DEV) run --rm reports $(ARGS)

dev-test: $(addprefix dev-test-,$(SERVICES))

dev-test-%:
	$(COMPOSE_DEV) run --rm --no-deps --entrypoint pytest $* $(ARGS)

dev-sim-up:
	$(COMPOSE_DEV) up -d --wait scan-simulator

dev-sim-down:
	$(COMPOSE_DEV) rm -sf scan-simulator

dev-sim-restart:
	$(COMPOSE_DEV) up -d --force-recreate --wait scan-simulator

dev-sim-status:
	$(COMPOSE_DEV) ps scan-simulator

dev-sim-logs:
	$(COMPOSE_DEV) logs -f scan-simulator

prod-build:
	$(COMPOSE_PROD) --profile services build

prod-up:
	$(COMPOSE_PROD) up -d mongo

prod-down:
	$(COMPOSE_PROD) --profile services down

prod-logs:
	$(COMPOSE_PROD) logs -f mongo

prod-sync:
	$(COMPOSE_PROD) run --rm -T interface-sync $(ARGS)

prod-collect:
	$(COMPOSE_PROD) run --rm -T traffic-collector $(ARGS)

prod-report:
	$(COMPOSE_PROD) run --rm -T reports $(ARGS)