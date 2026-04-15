SHELL := /bin/bash

VENV_NAME := fiap_ano2_fase2_cap1_venv
VENV_BIN  := $(VENV_NAME)/bin
PYTHON    := $(VENV_BIN)/python3
PIP       := $(VENV_BIN)/pip

.DEFAULT_GOAL := all

.PHONY: all prep-venv shell jupyter datasets clean

all: prep-venv
	source $(VENV_BIN)/activate && /bin/bash

prep-venv:
	python3 -m venv $(VENV_NAME)
	$(PIP) install --upgrade pip --quiet
	$(PIP) install -r requirements.txt --quiet

jupyter:
	source $(VENV_BIN)/activate && jupyter notebook notebooks/

datasets:
	source $(VENV_BIN)/activate && $(PYTHON) scripts/create_combined_dataset.py

clean:
	-rm -rf $(VENV_NAME)
