# Backend

The backend and API for D-sektionens member services.

The project is built using [Django](https://www.djangoproject.com/) (Python).

Use standard CPython 3.14.10 (with the GIL enabled) and uv 0.13.8 or newer.
Run `uv sync --locked` to install the development environment, and use
`uv run python manage.py test` with PostgreSQL configured to run the full suite.
`TEST_DATABASE=sqlite uv run python manage.py test` is a quick alternative that
skips PostgreSQL-specific checks. CI's legacy `3.12` job labels are retained
because branch protection requires those names; the jobs run Python 3.14.10.
Email HTML uses the original `minify-html` package from PyPI.

Microsoft Entra login uses MSAL's authorization-code flow. Set `CLIENT_ID`,
`CLIENT_SECRET`, `LIU_TENANT_ID`, and `BASE_URL`; register
`<BASE_URL>/oauth2/callback` as the application's Web redirect URI in Entra.
Pending login flows live in server-side Django sessions. Graph tokens are used
only to load the profile at login; API authentication uses the existing JWT
cookies. Logout ends the local session without signing the user out of Entra.

Email uses Django's `MAILERS` configuration. The default mailer queues through
Post Office; queued delivery uses the `smtp` mailer with `EMAIL_HOST`,
`EMAIL_PORT`, `EMAIL_USER`, and `EMAIL_PASSWORD` (STARTTLS, default port 587).
Budget emails use the separate `budget` mailer. Set `BUDGET_EMAIL_PASSWORD`
before deploying; `BUDGET_EMAIL_HOST`, `BUDGET_EMAIL_PORT`, and
`BUDGET_EMAIL_USER` can override the defaults shown in `.env.sample`.
The budget sender address remains `noreply.budget@d-sektionen.se`.

As a WebbU member, refer to the [Wiki](https://github.com/d-sektionen/.github-private/wiki/backend.d-sektionen.se) for more documentation.
