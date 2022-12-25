.PHONY: help lint clean_pycache testpublish publish

# .DEFAULT_GOAL := help

help:
	@echo "boardman development cli"

lint:
	pre-commit run --all-files

clean_pycache:
	find . | grep -E "(/__pycache__$$|\.pyc$$|\.pyo$$)" | xargs rm -vrf

testpublish:
	rm -rf dist/boardman*[.tar.gz,.whl] \
 && poetry publish -vvv --build -r testpypi

publish:
	rm -rf dist/boardman*[.tar.gz,.whl] \
 && poetry publish -vvv --build
