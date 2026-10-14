.PHONY: all validate test orchestrate decisions-init decisions-report clean

all: validate test

validate:
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
