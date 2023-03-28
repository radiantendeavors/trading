# ----------------------------------------------------------------------
#
# Makefile for trader
#
# By G S Derber
#
#
#
# ---------------------------------------------------------------------
NAME=trader
VERSION=0.1.1


# -------
#
# Global Variables
#
# -------
BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
ifeq (Branch, main)
	VENV_DIR := $(HOME)/.local/lib/pytrader_stable
else
	VENV_DIR := $(HOME)/.local/lib/pytrader_development
endif

PYTHON := /usr/bin/python3
VENV := $(PYTHON) -m venv $(VENV_DIR)
PIP := $(VENV_DIR)/bin/pip

#COLORS
GREEN  := $(shell tput -Txterm setaf 2)
WHITE  := $(shell tput -Txterm setaf 7)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
# A category can be added with @category
HELP_FUN = \
    %help; \
    while(<>) { push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([0-9a-zA-Z\-]+)\s*:.*\#\#(?:@([a-zA-Z\-]+))?\s(.*)$$/ }; \
    print "USAGE\n\nmake [target]\n\n"; \
    for (sort keys %help) { \
    print "${WHITE}$$_:${RESET}\n"; \
    for (@{$$help{$$_}}) { \
    $$sep = " " x (16 - length $$_->[0]); \
    print "  ${YELLOW}$$_->[0]${RESET}$$sep${GREEN}$$_->[1]${RESET}\n"; \
    }; \
    print "\n"; }

help: ##@other Show this help.
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

# C++ Related targets
build: ##@CPP
	@mkdir build
	@cd build && cmake .. && cmake --build

cleancpp: ##@Clean Cleans up C++ Build files
	@rm -rf build

# Python related targets
venv: ##@Python Creates Python VENV
	@mkdir -p $(VENV_DIR)
	@$(VENV)

setup: venv ##@Python Installs required packages
	$(PIP) install -r requirements.txt

requirements: ##@Python Creates requirements.txt
	@$(PIP) freeze > requirements.txt

clean_venv:
	@rm -rf $(VENV_DIR)

cleanpython: ##@Clean Cleans up python cache files
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

# Combined targets
clean: cleancpp cleanpython ##@Clean

.PHONY: all clean
