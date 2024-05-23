# Testing
All apps should have a tests dir where all tests and related logic is stored. Unless there's a good reason not to each test class should inherit from AuthenticatedTestCase. Inheriting from this class automatically creates users with different privileges for use in the tests.

Tests can be run with the following command:
`python manage.py test`

A tests for a specific app can be run by specifying it in the command:
`python manage.py test voting`

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

