.PHONY: venv

venv:
	python3.13 -m venv .env
	. .env/bin/activate
	./.env/bin/python -m pip install -r requirements.txt
	./.env/bin/python -m pip install -e .
