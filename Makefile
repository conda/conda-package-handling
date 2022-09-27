style:             ## Style code with isort/black
	@isort --profile black .
	@black -l 99 --skip-magic-trailing-comma .
