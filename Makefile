.PHONY: build-dev up-dev down-dev build-prod up-prod down-prod migrate shell collectstatic setup-dev setup-prod clean backup backup-dev backup-prod setup-backup-cron remove-backup-cron build-local up-local down-local

# Setup commands
setup-dev:
	chmod +x docker/dev/entrypoint.sh

clean-dev:
	docker-compose -f docker/dev/docker-compose.yml down
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete

# Update build-dev to use clean
build-dev: clean-dev setup-dev
	docker-compose -f docker/dev/docker-compose.yml build

up-dev: build-dev
	docker-compose -f docker/dev/docker-compose.yml up -d

down-dev:
	docker-compose -f docker/dev/docker-compose.yml down


migrate-dev:
	docker-compose -f docker/dev/docker-compose.yml run --rm web python manage.py migrate

shell-dev:
	docker-compose -f docker/dev/docker-compose.yml run --rm web python manage.py shell

collectstatic-dev:
	docker-compose -f docker/dev/docker-compose.yml run --rm web python manage.py collectstatic --noinput

bash-dev:
	docker-compose -f docker/dev/docker-compose.yml run --rm web bash

up-dev-n8n:
	docker-compose -f docker/dev/docker-compose.n8n.yml up -d
	
down-dev-n8n:
	docker-compose -f docker/dev/docker-compose.n8n.yml down -v

dump-data-dev:
	docker-compose -f docker/dev/docker-compose.yml run --rm web python manage.py json_dumper sekurah_data

up-dev-frontend:
	docker-compose -f docker/dev/docker-compose.yml up -d frontend

down-dev-frontend:
	docker-compose -f docker/dev/docker-compose.yml stop frontend

deploy-dev: build-dev up-dev up-dev-frontend
	echo "Deploying development environment with frontend..."

# Local development commands
build-local:
	docker-compose -f docker/local/docker-compose.yml build

up-local: build-local
	docker-compose -f docker/local/docker-compose.yml up -d

down-local:
	docker-compose -f docker/local/docker-compose.yml down

migrate-local:
	docker-compose -f docker/local/docker-compose.yml run --rm web python manage.py migrate

shell-local:
	docker-compose -f docker/local/docker-compose.yml run --rm web python manage.py shell

bash-local:
	docker-compose -f docker/local/docker-compose.yml run --rm web bash

up-local-frontend:
	docker-compose -f docker/local/docker-compose.yml up -d frontend

# Backup commands
backup-dev:
	chmod +x ./db_backup.sh
	./db_backup.sh --env-file docker/dev/.env --output-dir ./backups/dev

backup-prod:
	chmod +x ./db_backup.sh
	./db_backup.sh --env-file docker/prod/.env --output-dir ./backups/prod

# Default backup uses production environment
backup: backup-prod

# Cron job setup for automated backups every 6 hours
setup-backup-cron:
	@echo "Setting up cron job to run backups every 6 hours..."
	@chmod +x ./db_backup.sh
	@WORKSPACE_DIR=$(shell pwd)
	@(crontab -l 2>/dev/null || echo "") | grep -v "db_backup.sh" > temp_cron
	@echo "0 */6 * * * cd $(shell pwd) && ./db_backup.sh --env-file docker/prod/.env --output-dir $(shell pwd)/backups/prod >> $(shell pwd)/backups/backup.log 2>&1" >> temp_cron
	@crontab temp_cron
	@rm temp_cron
	@echo "Cron job installed. Backups will run every 6 hours and logs will be saved to $(shell pwd)/backups/backup.log"
	@mkdir -p $(shell pwd)/backups
	@touch $(shell pwd)/backups/backup.log
	@echo "You can view the cron jobs with: crontab -l"

# Remove backup cron job
remove-backup-cron:
	@echo "Removing backup cron job..."
	@(crontab -l 2>/dev/null | grep -v "db_backup.sh") > temp_cron
	@crontab temp_cron
	@rm temp_cron
	@echo "Backup cron job removed."

# Production commands
clean-prod:
	docker-compose -f docker/prod/docker-compose.yml down
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete

setup-prod:
	chmod +x docker/prod/entrypoint.sh

build-prod: clean-prod setup-prod
	rm -rf docker/prod/static
	rm -rf docker/prod/media
	docker-compose -f docker/prod/docker-compose.yml build

up-prod: build-prod
	docker-compose -f docker/prod/docker-compose.yml up -d
	docker-compose -f docker/prod/docker-compose.yml run --rm web python manage.py migrate django_celery_beat
	docker-compose -f docker/prod/docker-compose.yml run --rm web python manage.py migrate_schemas --fake-initial

down-prod:
	docker-compose -f docker/prod/docker-compose.yml down

migrate-prod:
	docker-compose -f docker/prod/docker-compose.yml run --rm web python manage.py migrate

shell-prod:
	docker-compose -f docker/prod/docker-compose.yml run --rm web python manage.py shell

collectstatic-prod:
	docker-compose -f docker/prod/docker-compose.yml run --rm web python manage.py collectstatic --noinput

bash-prod:
	docker-compose -f docker/prod/docker-compose.yml run --rm web bash

up-prod-n8n:
	docker-compose -f docker/prod/docker-compose.n8n.yml up -d

down-prod-n8n:
	docker-compose -f docker/prod/docker-compose.n8n.yml down -v

dump-data-prod:
	docker-compose -f docker/prod/docker-compose.yml run --rm web python manage.py json_dumper sekurah_data


deploy-prod: down-prod up-prod
	echo "Deploying production environment..."

