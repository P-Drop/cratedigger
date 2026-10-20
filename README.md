# Crate Digger

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
![Python](https://img.shields.io/badge/python-3.13-blue)
[![CI](https://github.com/P-Drop/cratedigger/actions/workflows/ci.yaml/badge.svg?branch=main&event=push)](https://github.com/P-Drop/cratedigger/actions/workflows/ci.yaml?query=branch%3Amain)

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
- [Contribute](#contribute)
    - [Why merge commits?](#why-merge-commits)
    - [Protected base branch](#protected-base-branch)
    - [Secret protection](#secret-protection)
    - [Dependency updates](#dependency-updates)
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
| CI | **GitHub Actions**: quality, secret scan, unit and integration tests, combined coverage >= 85%, commit message and PR title checks | ✅ |
| Dependencies | **Renovate** | ✅ |
| API Client | **Bruno** | ⌛️ |


> Note: MongoDB runs on 7.0 instead of 8: the mongo:8 image fails on recent Linux kernels ([SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912)). Upgrade pending until the issue is resolved.


## Install

### Requirements

- uv v0.12.19 (exact version, pinned in `pyproject.toml`).

    [Install uv from Astral](https://docs.astral.sh/uv/getting-started/installation/).

- Docker Engine v25.0.0 or later
- Docker Compose v2.20.2 or later

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

6. Install pre-commit hooks:

```bash
uv run pre-commit install
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

> WARNING: This command deletes ALL data in your local databases

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

## Contribute

Contributors are welcome!

Here's some info about development workflow and accepted PRs. Please, follow these steps:

1. Work on a feature branch, never on `main`. Use an existing branch or create a new one like this:

```bash
# To develop a new feature
git switch -c feat/<brief-branch-name>

# To fix bugs
git switch -c fix/<brief-branch-name>
```

2. Use atomic commits with Conventional Commits and subjects up to 72 characters. The same rules apply to the PR title. Fill in the PR body following the template and make sure you have completed all checks.

3. Verify your CI run passes all checks.

4. You will be notified when your PR is merged into main. Then, this branch is deleted automatically.

### Why merge commits?

This project merges PRs with *merge commits*. All atomic commits from a development branch reach `main`, so the history tracks progress commit by commit, while each merge commit groups a whole PR. Here, a PR usually covers a full phase, with several topics.

Use `git log --first-parent` to read the history by phase, and `bisect` / `blame` for commit-level detail.

Since every branch commit lands in `main`, make sure your commits are clean and follow Conventional Commits before asking for review.

### Protected base branch

`main` is protected by a ruleset that applies to all users, admin included:

- Changes only through a PR. Direct pushes, *force push* and branch deletion are forbidden.

- The branch must be up to date with `main` before merging. Update it with rebase, never with a merge:

```bash
git fetch origin

git rebase origin/main

git push --force-with-lease
```

- Required checks:
    - Check code quality.
    - Detect leaked secrets.
    - Unit tests.
    - Integration tests.
    - Check coverage threshold.
    - Check commit messages.
    - Check PR title.

- Commit messages and the PR title (the merge commit subject) follow the same rules, enforced in CI by `.github/scripts/check-message.sh`: Conventional Commits, subjects up to 72 characters, no autosquash commits (`fixup!`, `squash!`, `amend!`) and no messages starting with `Merge`. Merge commits inside the branch are rejected too.

    > The local hook still accepts `fixup!` commits, so you can use `git commit --fixup` while you work. Squash them with `git rebase -i --autosquash origin/main` before pushing.

- PRs from forks require admin approval before CI runs.

### Secret protection

1. Local gitleaks pre-commit.
2. GitHub *push protection*.
3. Gitleaks job over full history, which blocks merging.
4. *Secret scanning* monitoring repository.

The CI uses no secrets.

### Dependency updates

- Renovate reviews updates weekly.

- **Dashboard approval required** for *majors* and Python version changes.

- **Mongo** image stays below major version 8.

- **gitleaks hash**: Manually update `GITLEAKS_SHA256` with release `checksums.txt` for each update. Renovate automatically updates `GITLEAKS_VERSION` and hook `rev`, but this PR will fail intentionally until `GITLEAKS_SHA256` is updated.

- **Local uv**: Renovate automatically syncs `required-version` and hook `rev`, but this exact version must be available in local environment.

## License

Distributed under the MIT license. See [LICENSE](LICENSE).
