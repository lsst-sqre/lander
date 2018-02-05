.PHONY: help ldm151

help:
	@echo "Make command reference"
	@echo "  make ldm151 ...... (run LDM-151 integration test)"

ldm151:
	# End-to-end smoke integration test with LDM-151
	bash integration-tests/test_ldm151.bash
