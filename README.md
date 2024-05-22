# Fenix

## Install

```bash
$ poetry install
```

## Migrations

```bash
$ cd api/python_testing
$ poetry run alembic upgrade head
```

## Running the API

```bash
$ cd api
$ poetry run fastapi dev main.py
```

## Running the tests

```bash
$ poetry run coverage run -m pytest
```

## Generating the coverage report

```bash
$ poetry run coverage html