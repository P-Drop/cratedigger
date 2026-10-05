# Crate Digger

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
![Python](https://img.shields.io/badge/python-3.13-blue)

Crate Digger is a contribution to Hip Hop Roots and Culture.

It provides a REST API with artists and releases, sampling registry and lyrics archive.

**Learn By Doing**

I work with Claude Code here, set up in *Learning* mode. Claude organizes and evaluates my progress, while I design, code, write tests and run all the commands. Learning process is available at [docs/tutorial](docs/tutorial/).

## Table of Contents

- [Crate Digger](#crate-digger)
- [Table of Contents](#table-of-contents)
- [Stack](#stack)
- [Install](#install)
    - [Requirements](#requirements)
- [Usage](#usage)
    - [Run server](#run-server)
    - [Check service health](#check-service-health)
    - [Reset services from scratch](#reset-services-from-scratch)
    - [Check quality](#check-quality)
    - [Run tests suite](#run-tests-suite)
- [License](#license)

## Stack

✅ Done | ⌛️ Pending

| Area | Technology | Status |
| --- | --- | --- |
| Language | **Python 3.13**, managed by **uv** venv | ✅ |
| Framework | **Django 5.2 LTS** | ✅ |
| API | DRF, drf-spectacular, django-filter, djangorestframework-simplejwt, djangorestframework-stubs | ⌛️ |
| Relational DB | **PostgreSQL 17** (psycopg 3) | ✅ |
| Documental DB | **MongoDB 7** with PyMongo | ✅ |
| Extras | **Redis**, **Celery**, deploy | ⌛️ |
| Quality | **uv**, **ruff** (linter and formatter), **mypy** strict with **django-stubs**, **pytest** with **pytest-django**, **pytest-cov** and **factory_boy**, **pre-commit** | ✅ |
| Infra | **Docker** + **Compose** | ✅ |
| CI | **GitHub Actions** | ⌛️ |
| API Client | **Bruno** | ⌛️ |


> Note: MongoDB runs on 7.0 instead of 8: the mongo:8 image fails on recent Linux kernels ([SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912)). Upgrade pending until the issue is resolved.


## Install

### Requirements

- uv v0.12.16+.

    [Install uv from Astral](https://docs.astral.sh/uv/getting-started/installation/).

- Docker
- Docker Compose v2+

---

Follow these steps to install Crate Digger:

1. Clone this repo to your local machine.

```bash
git clone https://github.com/P-Drop/cratedigger.git
```

2. Get into project's root path and synchronize dependencies:

```bash
cd cratedigger

uv sync
```

3. Copy and create `.env` file in project's root path:

```bash
cp .env.example .env
```

> Remember to generate and replace required values in .env (follow instructions in file .env.example)

4. Run docker compose to init PostgreSQL and Mongo DB services:

```bash
docker compose up -d --wait

# check both services are running and healthy
docker compose ps
```

5. Run migrations:

```bash
uv run python manage.py migrate
```

## Usage

> This project is on an early building phase currently. Future usage options will be updated.

### Run server

```bash
# Run server in http://127.0.0.1:8000
uv run python manage.py runserver
```

### Check service health

```bash
curl http://localhost:8000/health/
```

### Reset services from scratch

> CAUTION: This command deletes ALL data in your local databases

```bash
# Stops and deletes containers and data volumes
docker compose down -v

# Then, start Docker services again
docker compose up -d --wait

# Apply migrations to database
uv run python manage.py migrate

# Finally, run the server
uv run python manage.py runserver
```

### Check quality

```bash
# Linter
uv run ruff check .

# Formatter
uv run ruff format .

# Typing
uv run mypy .
```

### Run tests suite

```bash
uv run pytest
```

## License

Distributed under the MIT license. See [LICENSE](LICENSE)
