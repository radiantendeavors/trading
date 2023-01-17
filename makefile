# ----------------------------------------------------------------------
#
# Makefile for trader
#
# By Geoff S Derber
#
#
#
# ---------------------------------------------------------------------
NAME=trader
VERSION=0.0.3


# -------
#
# Global Variables
#
# -------
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
cleanpython: ##@Clean Cleans up python cache files
	@rm -rf __pycache__

venv: ##@Python Creates Python VENV
	python3 -m venv

setup: venv ##@Python Installs required packages
	./venv/bin/pip install -r requirements.txt

requirements:
	@cd pytrader && pip freeze > requirements.txt

# Combined targets
clean: cleancpp cleanpython ##@Clean

.PHONY: all clean
