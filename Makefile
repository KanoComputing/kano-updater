# Makefile
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Standard interface to work with the project.


REPORT_DIR = reports
COVERAGE_REPORT_DIR = $(REPORT_DIR)/coverage
TESTS_REPORT_DIR = $(REPORT_DIR)/tests

# Elaborate mechanism just to get the correct syntax for the pytest markers param
_FIRST_TAG := $(firstword $(OMITTED_TAGS))
PYTEST_TAGS_EXPR := $(foreach tag, $(OMITTED_TAGS), $(if $(filter $(tag), $(_FIRST_TAG)),not $(tag),and not $(tag)))

ifeq ($(PYTEST_TAGS_EXPR), )
	PYTEST_TAGS_FLAG :=
else
	PYTEST_TAGS_FLAG := -m "$(strip $(PYTEST_TAGS_EXPR))"
endif
BEHAVE_TAGS_FLAG := $(join $(addprefix --tags=-,$(OMITTED_TAGS)), $(space))



.PHONY: clean docs


clean:
	cd docs && make clean

docs:
	cd docs && make all

check:
	# Refresh the reports directory
	rm -rf $(REPORT_DIR)
	mkdir -p $(REPORT_DIR)
	mkdir -p $(COVERAGE_REPORT_DIR)
	mkdir -p $(TESTS_REPORT_DIR)
	# Run the tests
	-coverage run --module pytest $(PYTEST_TAGS_FLAG) --junitxml=$(TESTS_REPORT_DIR)/pytest_results.xml
	-coverage run --append --module behave $(BEHAVE_TAGS_FLAG) --junit --junit-directory=$(TESTS_REPORT_DIR)
	# Generate reports
	coverage xml
	coverage html
	coverage-badge -o $(COVERAGE_REPORT_DIR)/kano-updater-coverage.svg

test: check
