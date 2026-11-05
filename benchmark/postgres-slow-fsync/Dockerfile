# PostgreSQL with artificially slow fsync, for benchmarking only.
# Same image as docker-compose.yml plus an LD_PRELOAD shim; see slowfsync.c.
FROM postgres:16.3-alpine AS build
RUN apk add --no-cache gcc musl-dev
COPY slowfsync.c /tmp/slowfsync.c
RUN gcc -shared -fPIC -O2 -o /usr/local/lib/slowfsync.so /tmp/slowfsync.c

FROM postgres:16.3-alpine
COPY --from=build /usr/local/lib/slowfsync.so /usr/local/lib/slowfsync.so
ENV LD_PRELOAD=/usr/local/lib/slowfsync.so
