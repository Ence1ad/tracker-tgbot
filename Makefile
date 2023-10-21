# Targets that do not represent files
.PHONY: down-all up-all up-core down-core hourly-pgbackup

all:
	@echo "up-all               -Rebuild and up all compose services."
	@echo "down-all             -Down all compose services"
	@echo "up-core              -Rebuild and up core compose services."
	@echo "down-core            -Down core compose services."
	@echo "hourly-pgbackup      -Set up hourly pg backup cron job."

up-all:
	docker compose -f docker-compose-monitoring.yml -f docker-compose-core.yml up --build

down-all:
	docker compose -f docker-compose-core.yml -f docker-compose-monitoring.yml down

up-core:
	docker compose -f docker-compose-core.yml up --build

down-core:
	docker compose -f docker-compose-core.yml down

hourly-pgbackup:
	sudo touch /var/log/pg_backup.log && sudo chown 1000:1000 /var/log/pg_backup.log
	(crontab -l ; echo "@hourly docker exec postgres_db bash /usr/bin/pg_backup_rotated.sh >> /var/log/pg_backup.log 2>&1") | crontab -

