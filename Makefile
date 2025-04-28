.PHONY: build-dev up-dev down-dev build-prod up-prod down-prod migrate shell collectstatic setup-dev setup-prod clean

# Setup commands
setup-dev:
	chmod +x docker/dev/entrypoint.sh

clean-dev:
	docker-compose -f docker/dev/docker-compose.yml down -v
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete

# Update build-dev to use clean
build-dev: clean setup-dev
	docker-compose -f docker/dev/docker-compose.yml build

up-dev: build-dev
	docker-compose -f docker/dev/docker-compose.yml up

down-dev:
	docker-compose -f docker/dev/docker-compose.yml down

migrate-dev:
	docker-compose -f docker/dev/docker-compose.yml run --rm web python manage.py migrate

shell-dev:
	docker-compose -f docker/dev/docker-compose.yml run --rm web python manage.py shell

collectstatic-dev:
	docker-compose -f docker/dev/docker-compose.yml run --rm web python manage.py collectstatic --noinput

deploy-dev: build-dev up-dev migrate-dev collectstatic-dev
	echo "Deploying development environment..."



# Production commands
setup-prod:
	chmod +x docker/prod/entrypoint.sh

clean-prod:
	docker-compose -f docker/prod/docker-compose.yml down
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	

build-prod: clean-prod
	docker-compose -f docker/prod/docker-compose.yml build

up-prod: build-prod
	docker-compose -f docker/prod/docker-compose.yml up -d

down-prod:
	docker-compose -f docker/prod/docker-compose.yml down

migrate-prod:
	docker-compose -f docker/prod/docker-compose.yml run --rm web python manage.py migrate

shell-prod:
	docker-compose -f docker/prod/docker-compose.yml run --rm web python manage.py shell

collectstatic-prod:
	docker-compose -f docker/prod/docker-compose.yml run --rm web python manage.py collectstatic --noinput

deploy-prod: up-prod migrate-prod collectstatic-prod
	echo "Deploying production environment..."