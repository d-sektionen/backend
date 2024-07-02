# Locks
This app has endpoints and functionality related to the smart locks used on our rented rooms. The app contacts the Yale API directly through the use of the library `yalexs`.
## Development
**Before adding any new functionality, make sure to read the documentation for [yalexs](https://github.com/bdraco/yalexs).**

It is recommended to use your own Yale account for testing. If you don't have an account, ask the Webmaster for an invite. Once you have one, you can acquire a valid token through the management command `authenticate_yale`:

```
./manage.py authenticate_yale
```

It will guide you through the authentication process, including 2fa. Once authenticated, a file called `.YALE_TOKEN_CACHE` will be created in the root directory. This is all you need to make authenticated requests to the API.

**Not working?** Remember to specify `YALE_EMAIL` and `YALE_PASSWORD` in the `.env` file
