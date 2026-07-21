VENV = .venv
PYTHON = $(VENV)/bin/python

IMAGE_NAME := scanbackup
IMAGE_TAG  := latest
IMAGE      := $(IMAGE_NAME):$(IMAGE_TAG)
TAR_FILE   := $(IMAGE_NAME).tar

UID := $(shell id -u)
GID := $(shell id -g)

CONFIG_FILE := $(CURDIR)/config.yml
DATA_DIR    := $(CURDIR)/data

.PHONY: updater test build package load run clean

updater:
	$(PYTHON) -m scanbackup sources traffic-export --dirpath ./data/sources

test:
	$(PYTHON) -m unittest discover -s tests -t . -v

build:
	docker build --build-arg UID=$(UID) --build-arg GID=$(GID) -t $(IMAGE) .

package: build
	docker save -o $(TAR_FILE) $(IMAGE)

load:
	docker load -i $(TAR_FILE)

run:
	docker run --rm \
		-v "$(CONFIG_FILE):/app/config.yml:ro" \
		-v "$(DATA_DIR):/app/data" \
		$(IMAGE) $(ARGS)

clean:
	rm -f $(TAR_FILE)
	docker rmi $(IMAGE) 2>/dev/null || true
