.PHONY: all validate test orchestrate decisions-init decisions-report clean

all: validate test

validate: validate-profiles
	@echo "== running monorepo linter =="
	python3 tooling/validate_tree.py

test:
	@echo "== running full-stack diagnostic =="
	python3 integration/test_full_stack_diagnostic.py

orchestrate:
	@echo "== running master pipeline =="
	python3 tooling/master_orchestrator.py

decisions-init:
	@python3 tooling/decisions/init_workbook.py

decisions-report:
	@python3 tooling/decisions/closure.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info .pytest_cache/

web-gen:
	python3 tooling/frontend/gen_frontend.py

web-validate: web-gen
	python3 tooling/validate_frontend.py

web-install: web-validate
	npm install --no-audit --no-fund

web-test: web-install
	npm run test

web-build: web-test
	npm run build
	python3 tooling/seal_frontend.py

validate-profiles:
	python3 tooling/validate_profiles.py

validate: validate-profiles

platform-validate:
	python3 tooling/platform_validate.py


federation-gate:
	python3 tooling/check_federation_gate.py
