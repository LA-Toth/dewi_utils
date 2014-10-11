include Makefile.vars

.PHONY: tests
tests:
	$(NOSE) -s $(NOSE_TEST_PATHS)
