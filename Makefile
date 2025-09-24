# Makefile — build datasets, servir dashboard e empacotar em Docker
.RECIPEPREFIX := >
SHELL := /usr/bin/env bash

PYTHON       ?= python3
PIP          ?= pip3
DOCKER       ?= docker
PORT         ?= 8000
DATA_INPUT   ?= data/master.xls
DATA_OUTPUT  ?= web/datasets
BUILD_SCRIPT := src/construir_datasets.py
IMAGE      ?= carlosrabelo/tabula
TAG        ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo latest)
FULL       := $(IMAGE):$(TAG)
LATEST     := $(IMAGE):latest
HOST_DATA_DIR ?=
HOST_DATASETS_DIR ?=
SYNC_DEST ?=
RSYNC_FLAGS ?= -av --delete
DOCKER_DATA_VOLUME := $(if $(HOST_DATA_DIR),-v $(HOST_DATA_DIR):/data:ro,)
DOCKER_DATASETS_VOLUME := $(if $(HOST_DATASETS_DIR),-v $(HOST_DATASETS_DIR):/app/web/datasets,)

.DEFAULT_GOAL := help

.PHONY: help install datasets serve docker-build docker-run docker-push docker-tag docker-shell sync-web clean clean-datasets

help:
> @echo ""
> @echo "Targets disponíveis para este projeto:"
> @echo "  install        - instala dependências Python locais (pandas/xlrd/openpyxl)"
> @echo "  datasets       - processa data/master.xls e gera CSVs em $(DATA_OUTPUT)"
> @echo "  serve          - roda um servidor estático via python -m http.server (porta $(PORT))"
> @echo "  docker-build   - builda a imagem $(FULL) com HTML placeholder (sem datasets)"
> @echo "  docker-run     - executa a imagem em modo interativo expondo a porta $(PORT)"
> @echo "  docker-push    - envia a imagem para o registry configurado em IMAGE"
> @echo "  docker-shell   - abre um shell na imagem gerada"
> @echo "  sync-web       - usa rsync para publicar o conteúdo de web/ no destino configurado"
> @echo "  clean          - remove artefatos de build (datasets CSV)"
> @echo ""

install:
> if [ -d .venv ]; then \
>   ./.venv/bin/pip install --upgrade pip; \
>   ./.venv/bin/pip install -r requirements.txt; \
> else \
>   echo "[info] .venv não encontrado. Crie com: python -m venv .venv"; \
> fi

datasets:
> ./$(BUILD_SCRIPT) --in $(DATA_INPUT) --out $(DATA_OUTPUT)

serve: datasets
> @echo "Servindo web/ em http://localhost:$(PORT)"
> $(PYTHON) -m http.server $(PORT) --directory web

docker-build:
> $(DOCKER) build --build-arg PORT=$(PORT) -t $(FULL) .

docker-tag:
> $(DOCKER) tag $(FULL) $(LATEST)

docker-push: docker-build docker-tag
> $(DOCKER) push $(FULL)

docker-run:
> $(DOCKER) run --rm -it \
>   -e PORT=$(PORT) \
>   -e DATA_INPUT=/data/master.xls \
>   -e DATA_OUTPUT=/app/web/datasets \
>   -p $(PORT):$(PORT) \
>   $(DOCKER_DATA_VOLUME) \
>   $(DOCKER_DATASETS_VOLUME) \
>   $(FULL)

docker-shell:
> $(DOCKER) run --rm -it \
>   $(DOCKER_DATA_VOLUME) \
>   $(DOCKER_DATASETS_VOLUME) \
>   $(FULL) /bin/bash

sync-web:
> if [ -z "$(SYNC_DEST)" ]; then \
>   echo "[erro] Informe SYNC_DEST=user@host:/destino"; \
>   exit 1; \
> fi
> rsync $(RSYNC_FLAGS) web/ $(SYNC_DEST)

clean-datasets:
> rm -f $(DATA_OUTPUT)/*.csv

clean: clean-datasets
> find . -type d -name '__pycache__' -exec rm -rf {} +
