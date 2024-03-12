# Locks
This app has endpoints and functionality related to the smart locks used on our rented rooms. Currently it uses Seam API to integrate with a Yale Linus lock. The documentation can be found [here](https://docs.seam.co/latest/).

## Development
It is recommended to use a sandbox when developing as it allows to test on fake locks. It can be enabled when creating a new workspace in the Seam dashboard. It can be specified through the `SEAM_API_KEY` environment variable. Fake locks can be added using the fake login details [here](https://docs.seam.co/latest/developer-tools/sandbox-and-sample-data)
