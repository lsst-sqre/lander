.PHONY: help test pytest ldm151 dmtn070

help:
	@echo "Make command reference"
	@echo "  make test ........ (run all unit and integration tests)"
	@echo "  make pytest ...... (run pytest unit tests)"
	@echo "  make ldm151 ...... (run LDM-151 integration test)"
	@echo "  make ldm070 ...... (run DMTN-070 integration test)"

test: pytest ldm151 dmtn070

pytest:
	pytest --flake8 --doctest-modules lander tests

ldm151:
	# End-to-end smoke integration test with LDM-151
	bash integration-tests/test_ldm151.bash

dmtn070:
	# End-to-end smoke integration test with DMTN-070
	bash integration-tests/test_dmtn070.bash
