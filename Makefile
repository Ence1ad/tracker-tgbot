# Targets that do not represent files
.PHONY: down-all up-all up-core down-core

# Define the default target that will be executed if you just run "make" without specifying a target.
all:
	cat Makefile

# Define a target to rebuild and start containers.
up-all:
	docker compose -f docker-compose-monitoring.yml -f docker-compose-core.yml up --build

# Define a target to stop and remove containers.
down-all:
	docker compose -f docker-compose-core.yml -f docker-compose-monitoring.yml down
# Define a target to rebuild and start containers for core only.
up-core:
	docker compose -f docker-compose-core.yml up --build

down-core:
	docker compose -f docker-compose-core.yml down