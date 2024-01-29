POETRY=poetry
DOCKER=docker

ifeq ($(USE_POETRY), false)
	PYTEST=pytest
	MYPY=mypy --ignore-missing-imports
	BLACK=black
	ISORT=isort
	PYLINT=pylint
	UVICORN=uvicorn
	ALEMBIC=alembic
else
	PYTEST=$(POETRY) run pytest
	MYPY=$(POETRY) run mypy --ignore-missing-imports
	BLACK=$(POETRY) run black
	ISORT=$(POETRY) run isort
	PYLINT=$(POETRY) run pylint
	UVICORN=$(POETRY) run uvicorn
	ALEMBIC=$(POETRY) run alembic
endif

install:
	$(POETRY) install

update:
	$(POETRY) update
	$(POETRY_EXPORT)

test: install
	$(MYPY) main.py ./${PACKAGE}/
	$(PYTEST) -vv

fmt:
	$(ISORT) main.py . ./tests
	$(BLACK) main.py . ./tests

lint:
	$(PYLINT) main.py . ./tests

release:
	$(POETRY) install --no-dev --no-root --no-interaction --no-ansi
	$(POETRY_EXPORT)

dev:
	${UVICORN} main:app --reload

prod:
	${UVICORN} main:app --host=0.0.0.0 --port=${PORT}

migrate:
	${ALEMBIC} upgrade head

downgrade:
	${ALEMBIC} downgrade -1

REVISION_MESSAGE ?= $(shell bash -c 'read -p "Revision message: "  msg; echo $$msg')

revision:
	${ALEMBIC} revision -m "$(REVISION_MESSAGE)" --autogenerate