.PHONY: env up down health setup load benchmark backup charts analyze check validate clean-results

env:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@test -f .env || cp .env.example .env

up:
	docker compose up -d
	docker compose ps

down:
	docker compose down

health:
	docker compose ps

setup:
	.venv/bin/python -m benchmark.setup_databases

load:
	.venv/bin/python -m benchmark.load_data --orders $${ORDERS:-100000}

benchmark:
	.venv/bin/python -m benchmark.run_all --orders $${ORDERS:-100000} --repetitions $${REPETITIONS:-10}

backup:
	.venv/bin/python -m benchmark.backup_restore_benchmark

charts:
	.venv/bin/python -m benchmark.charts

analyze:
	.venv/bin/python -m benchmark.merge_results
	.venv/bin/python -m benchmark.analyze_results

check:
	.venv/bin/python -m compileall -q benchmark tests
	.venv/bin/python -m unittest discover -s tests -v
	docker compose config --quiet

validate:
	.venv/bin/python -m benchmark.validate_results
	$(MAKE) check

clean-results:
	find results -maxdepth 1 -type f \( -name '*.csv' -o -name '*.json' \) -delete
	find charts -maxdepth 1 -type f -name '*.png' -delete
