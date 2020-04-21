fmt:
	isort -rc scripts
	black scripts
	flake8 scripts