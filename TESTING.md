# Testing

All apps should have a tests dir where all tests and related logic is stored. Unless there's a good reason not to each test class should inherit from AuthenticatedTestCase. Inheriting from this class automatically creates users with different privileges for use in the tests.

Tests can be run with the following command:
`python manage.py test`

A tests for a specific app can be run by specifying it in the command:
`python manage.py test voting`

The tests run against Postgres, both locally and in CI, using the `POSTGRES_*` variables from `.env`. Some tests only work on Postgres and are skipped on other databases. With `docker compose up` running, the simplest way is to run them inside the backend container:

`docker compose exec backend python manage.py test`

To run them directly on your machine instead, point `POSTGRES_HOST` at the published port (`.env` uses the compose service name, which only resolves inside Docker):

`POSTGRES_HOST=localhost python manage.py test`

For a quick run without a database server, `TEST_DATABASE=sqlite python manage.py test` uses an in-memory SQLite database. The Postgres-only tests are then skipped, so do not rely on it before opening a PR.

The following libaries are used to test:

* [factory_boy](https://factoryboy.readthedocs.io/en/stable/)
* [Faker](https://faker.readthedocs.io/en/master/)

## Naming

Tests with the following strings appended to the name indicate:

* `as_member` - The test is performed as an authenticated member of the section.
* `as_non_member` - The test is performed as an authenticated user that does not have a membership (AKA near minimum privileges).
* `as_admin` - The test is performed as an admin. It has a membership and is a superuser (AKA has all privileges).

All test files must begin with `test_...` otherwise they will be ignored.

## Factories

Each test directory should contain a `Factories.py` file where applicable. This file should contain factories for all models, with exceptions where necessary. Mock as much data as possible with Faker!
