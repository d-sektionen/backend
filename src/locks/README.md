# Locks

This app has endpoints and functionality related to the smart locks used on our rented rooms. Currently it uses Home assistant as a middleware.

## Why Home Assistant?

Yale provides OAuth access exclusively to their partners. Since December 2024, the old API has been deprecated, and the new one requires OAuth. Therefore, we use Home Assistant as a middleware to utilize their OAuth access.

## Development

There are two alternatives for local development:

- Running a local instance of Home Assistant.
- Connecting to the production server using a SSH tunnel.
