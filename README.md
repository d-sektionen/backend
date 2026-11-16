# Backend

The backend and API for D-sektionens member services.

The project is built using [Django](https://www.djangoproject.com/) (Python).

Microsoft Entra login uses MSAL's authorization-code flow. Set `CLIENT_ID`,
`CLIENT_SECRET`, `LIU_TENANT_ID`, and `BASE_URL`; register
`<BASE_URL>/oauth2/callback` as the application's Web redirect URI in Entra.
Pending login flows live in server-side Django sessions. Graph tokens are used
only to load the profile at login; API authentication uses the existing JWT
cookies. Logout ends the local session without signing the user out of Entra.

As a WebbU member, refer to the [Wiki](https://github.com/d-sektionen/.github-private/wiki/backend.d-sektionen.se) for more documentation.
