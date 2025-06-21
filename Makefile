.PHONY: migrate up down

export DATABASE_URL=postgres://blog:blog@localhost:5432/blog

ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

$(eval $(ARGS):;@:)

migrate:
ifeq ($(firstword $(ARGS)),up)
	@echo "Applying migrations..."
	@sqlx migrate run
else ifeq ($(firstword $(ARGS)),down)
	@echo "Reverting migrations..."
	@sqlx migrate revert
else ifeq ($(firstword $(ARGS)),add)
	@sqlx migrate add -r $(wordlist 2,$(words $(ARGS)),$(ARGS))
else ifeq ($(firstword $(ARGS)),drop)
	@echo "Resetting database..."
	@sqlx database drop
else
	@echo "Usage: make migrate [up|down|drop|add <name>]"
	@exit 1
endif
