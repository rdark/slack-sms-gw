.PHONY: test clean bootstrap
package = slack_sms_gw

# test
test:
	mypy -p $(package) --ignore-missing-imports
	python -m pytest -vs

# remove pyc & __pycache__ files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

bootstrap:
	pip install -r requirements-test.txt
