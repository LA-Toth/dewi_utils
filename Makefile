include Makefile.vars

.PHONY: help
help:
	@echo "Available common targets:"
	@echo "check            --- check everything"
	@echo "tests            --- run Python unit tests"
	@echo "cs               --- run coding standards checks"
	@echo "pylint           --- run pylint checks only"
	@echo "pep8             --- run pep8 checks only"
	@echo "features         --- run behave scenarios without @wip tag"
	@echo "features-wip     --- run behave scenarios with @wip tag"

.PHONY: check
check: cs tests features

.PHONY: tests
tests:
	@echo Running Python unit tests
	$(NOSE) -s $(NOSE_TEST_PATHS)

.PHONY: cs
cs: pep8
	@echo Runing pylint
	export PYLINTHOME=$(PYLINT_DIR)
	mkdir -p $(PYLINT_DIR)
	PYTHONPATH=".:$(PYTHONPATH)" $(PYLINT) --rcfile=.pylintrc $(PACKAGE_NAMES)

.PHONY: codingstandards
codingstandards: pep8
	@echo Running pylint with reports
	export PYLINTHOME=$(PYLINT_DIR)
	mkdir -p $(PYLINT_DIR)
	PYTHONPATH=".:$(PYTHONPATH)" $(PYLINT) --report=yes --rcfile=.pylintrc $(PACKAGE_NAMES)

# Ignored errors:
#
# Code  Description                                               Reason for ignoring
# ----  -----------                                               -------------------
# E501  line too long                                             This is checked by pylint
# E126  continuation line over-indented for hanging indent        This is not a problem locally, helps readability
# E241  multiple spaces after ','                                 This is not a problem locally, helps readability
# E121  continuation line indentation is not a multiple of four   This is not a problem locally, helps readability
.PHONY: codestyle
codestyle:
	@echo "Running pycodestyle (pep8)"
	$(PYCODESTYLE) --ignore=E501,E126,E241,E121 --repeat $(PACKAGE_NAMES)

.PHONY: pep8
pep8: codestyle

.PHONY: features
features:
	@echo Running feature specifications - non-wip scenarios
	PYTHONPATH=features:$(PYTHONPATH) $(BEHAVE) --tags=-wip

.PHONY: features-wip
features-wip:
	@echo Running feature specifications - wip scenarios
	PYTHONPATH=features:$(PYTHONPATH) $(BEHAVE) --tags=wip
