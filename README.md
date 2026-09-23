# Ub'EJR Eats API

[![tests](https://github.com/no0e/ubjr-eats-api/actions/workflows/tests.yml/badge.svg)](https://github.com/no0e/ubjr-eats-api/actions/workflows/tests.yml)
[![python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/)
[![licence](https://img.shields.io/badge/licence-MIT-green)](LICENSE)

A food delivery backend: a FastAPI service over a layered architecture, with
three user roles, JWT authentication, PostgreSQL, and route planning for the
drivers.

The domain is a student-run restaurant at ENSAI taking orders for delivery.
Customers build a cart from the menu and order it; drivers see the pending
orders and get an itinerary that chains their stops; administrators manage
accounts and the menu.

## Architecture

Four layers, and no layer skips the one below it.

```
App/       FastAPI routers, one per role. HTTP in, HTTP out, nothing else.
Service/   the domain. Ordering, delivery routing, passwords, tokens.
DAO/       one class per table. Parameterised SQL, and nowhere else in the
           codebase writes SQL.
Model/     Pydantic models. The shape of a user, an order, a delivery.
```

The point of that separation shows up in the tests. `tests/Service` can check
that an order cannot be assigned to a driver who already has one, without a
database. `tests/DAO` can check that the SQL does what it says, against a real
PostgreSQL. Neither test has to pretend to be the other.

Authentication is a JWT carrying the username and role, validated by a FastAPI
dependency, so a route declares what it needs rather than checking it inline.
Passwords are salted per user, with a 256-character salt, and hashed.

## What runs it

| | |
|---|---|
| API | FastAPI, uvicorn, OpenAPI docs at `/` |
| Database | PostgreSQL, psycopg2, parameterised queries throughout |
| Auth | PyJWT, role-based dependencies, per-user salts |
| Routing | Google Maps Geocoding and Directions |
| Tests | pytest, 17 modules across the data and service layers |

## Running it

```bash
git clone https://github.com/no0e/ubjr-eats-api.git
cd ubjr-eats-api
pip install -r requirements.txt

cp .env.sample .env      # then fill it in
python -c "from src.Utils.reset_db import ResetDatabase; ResetDatabase().launch(); ResetDatabase().launch(True)"
python __main__.py
```

The API comes up on port 8000 and redirects to its own documentation.

`.env` needs PostgreSQL connection details, a `JWT_SECRET`, and a
`GOOGLE_MAPS_API_KEY` with the Geocoding and Directions APIs enabled. Without
the Google key everything works except the driver itinerary, which raises a
message saying which variable is missing rather than failing at import.

```bash
pytest tests/ -q
```

The service tests run without anything else. The DAO tests need the database up
and the schemas loaded, which is what the two `ResetDatabase` calls above do;
CI brings a PostgreSQL container up beside the suite for exactly that reason.

## About this repository

This is a rewrite of a team project built at ENSAI over fifteen months by four
developers: **Justine Oliviero**, **Tristan Talbot**, **Noe Diette** and
**Emma Glorieux**, from a template by Clement Valot. The original repository
holds the full history, 517 commits, and is the record of who wrote what.

What this repository changes:

- the Google Maps API key, which was a literal in the source and therefore in
  the git history, is now read from the environment at call time;
- `DBConnector` read `config["port"]` from a key spelled `"post"`, so passing
  an explicit config raised `KeyError` and only the environment path worked;
- a failed query printed `ERROR` to stdout and re-raised; it now logs;
- `UserService` built its own Google client and geocoded an address inside
  `create_user`, so creating a user needed a network call and a paid key, and
  two service tests could not run without one. It now takes the geocoder by
  injection, the way `DeliveryService` already did, and those tests pass a
  fake. Moving the key out of the source is what made this visible;
- `requirements.txt` was a full freeze of a development environment, 185 lines
  including an AWS client and a database migration tool that nothing imports.
  It is now the eleven packages the code actually uses;
- CI runs the suite against a real PostgreSQL, which the project never had.

## License

MIT. See [LICENSE](LICENSE).
