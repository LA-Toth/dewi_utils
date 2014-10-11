include Makefile.vars

.PHONY: tests
tests:
	$(NOSE) -s $(NOSE_TEST_PATHS)

.PHONY: cs
cs: pep8
	export PYLINTHOME=$(PYLINT_DIR)
	mkdir -p $(PYLINT_DIR)
	PYTHONPATH=".:$(PYTHONPATH)" $(PYLINT) --rcfile=.pylintrc $(PACKAGE_NAMES)

.PHONY: codingstandards
codingstandards: pep8
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
.PHONY: pep8
pep8:
	$(PEP8) --ignore=E501,E126,E241,E121 --repeat $(PACKAGE_NAMES)
