# Locks

This app has endpoints and functionality related to the smart locks used on our rented rooms. Currently it uses Home assistant as a middleware.

## Why Home Assistant?

Yale provides OAuth access exclusively to their partners. Since December 2024, the old API has been deprecated, and the new one requires OAuth. Therefore, we use Home Assistant as a middleware to utilize their OAuth access.

## Development

There are two alternatives for local development:

- Running a local instance of Home Assistant. For example through the docker [image](https://hub.docker.com/r/homeassistant/home-assistant).
- Connecting to the production server using a SSH tunnel (on port 8123). A ready-made script is available [here](https://github.com/d-sektionen/d-sektionen-server/blob/nyserver/bin/ssh_tunnel)

You then need to get an access token from Home Assistant. This can be done by following the instructions [here](https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token)

Once a token is acquired, it should be stored in the environment variable `HOME_ASSISTANT_TOKEN`.
