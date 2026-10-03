test:
	pytest -q
lint:
	ruff check .
run:
	uvicorn app.main:app --reload
