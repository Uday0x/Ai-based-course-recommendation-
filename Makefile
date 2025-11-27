.PHONY: train up build run test

train:
	python3 backend/scripts/train.py --output backend/models --n-samples 5000

up:
	docker-compose up --build

build:
	docker-compose build

run:
	cd backend && uvicorn app.main:app --reload --port 8000

test:
	pytest -q