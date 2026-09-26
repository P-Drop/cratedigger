# Crate Digger

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
![Python](https://img.shields.io/badge/python-3.13-blue)

Crate Digger is a contribution to Hip Hop Roots and Culture.

It provides an API REST with artists and releases, sampling registry and lyrics archive.

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
    - [Check quality](#check-quality)
    - [Run tests suite](#run-tests-suite)
- [License](#license)

## Stack

✅ Done | ⌛️ Pending

| Area | Technology | Status |
| --- | --- |
| Language | **Python 3.13**, managed by **uv** venv | ✅ |
| Framework | **Django 5.2 LTS** | ✅ |
| API | DRF, drf-spectacular, django-filter, djangorestframework-simplejwt | ⌛️ |
| Relational DB | **PostgreSQL 17** (psycopg 3) | ⌛️ |
| Documental DB | **MongoDB 8** with PyMongo | ⌛️ |
| Extras | **Redis**, **Celery**, deploy | ⌛️ |
| Quality | **uv**, **ruff** (linter and formatter), **mypy** strict with **django-stubs** and **djangorestframework-stubs**, **pytest** with **pytest-django**, **pytest-cov** and **factory_boy**, **pre-commit** | ✅ |
| Infra | **Docker** + **Compose**, **GitHub Actions** | ⌛️ |
| API Client | **Bruno** | ⌛️ |


## Install

### Requirements

- uv v0.12.16+.

    [Install uv from Astral](https://docs.astral.sh/uv/getting-started/installation/).

- Docker

---

Follow these steps to install Crate Digger:

1. Clone this repo to your local machine.

2. Get into project's root path and synchronize dependencies:

```bash
cd cratedigger

uv sync
```

3. Copy and create `.env` file in project's root path:

```bash
cp .env.example .env
```

## Usage

> This project is on an early building phase currently. Future usage options will be updated.

### Run server

```bash
cd cratedigger

# Run server in http://127.0.0.1:8000
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

Distributed by MIT license. See [LICENSE](LICENSE)
