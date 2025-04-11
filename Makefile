.PHONY: build-dev up-dev down-dev build-prod up-prod down-prod migrate shell collectstatic setup-dev setup-prod clean

# Setup commands
setup-dev:
	chmod +x docker/dev/entrypoint.sh

setup-prod:
	chmod +x docker/prod/entrypoint.sh

# Development commands
# Cleanup command
clean:
	docker-compose -f docker/dev/docker-compose.yml down -v
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete

# Update build-dev to use clean
build-dev: clean setup-dev
	docker-compose -f docker/dev/docker-compose.yml build

up-dev: setup-dev
	docker-compose -f docker/dev/docker-compose.yml up

down-dev:
	docker-compose -f docker/dev/docker-compose.yml down

# Production commands
build-prod:
	docker-compose -f docker/prod/docker-compose.yml build

up-prod:
	docker-compose -f docker/prod/docker-compose.yml up -d

down-prod:
	docker-compose -f docker/prod/docker-compose.yml down

# Django commands
migrate:
	docker-compose -f docker/dev/docker-compose.yml run --rm web python manage.py migrate

shell:
	docker-compose -f docker/dev/docker-compose.yml run --rm web python manage.py shell

collectstatic:
	docker-compose -f docker/dev/docker-compose.yml run --rm web python manage.py collectstatic --noinput