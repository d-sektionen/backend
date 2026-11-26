# Voting benchmark

Reproduces the production symptom (vote casting backs up on slow storage) on
a laptop, so changes can be measured before and after.

`compose.bench.yml` overlays the development stack with a PostgreSQL image
whose `fsync`/`fdatasync` calls sleep `FSYNC_DELAY_MS` milliseconds (see
`postgres-slow-fsync/`), and runs the backend with four worker processes like
production. `python manage.py bench_voting` seeds a meeting with voting
members, casts one vote per member concurrently over HTTP, prints latency and
throughput, and removes the seeded data again.

```sh
export FSYNC_DELAY_MS=20   # set in .env or the environment; 0 = normal disk
docker compose -f docker-compose.yml -f compose.bench.yml up -d --build postgres redis backend
docker compose -f docker-compose.yml -f compose.bench.yml exec backend \
    python manage.py bench_voting --voters 200 --concurrency 50 --rounds 3
docker compose -f docker-compose.yml -f compose.bench.yml down -v
```

Compare branches by checking out the other branch and restarting the
`backend` service (the code is bind-mounted); the database keeps its
migrations, so run `python manage.py migrate` inside the container when the
schema differs.
