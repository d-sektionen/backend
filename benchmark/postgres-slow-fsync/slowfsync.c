/*
 * LD_PRELOAD shim that adds latency to every fsync()/fdatasync() call, so a
 * fast local disk behaves like slow network-attached storage for PostgreSQL.
 * Every committed transaction waits for one of these calls (WAL flush), which
 * is the cost this benchmark is about.
 *
 * FSYNC_DELAY_MS: milliseconds added per call (default 0 = passthrough).
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdlib.h>
#include <time.h>

static long delay_ms = -1;

static void delay(void) {
    if (delay_ms < 0) {
        const char *value = getenv("FSYNC_DELAY_MS");
        delay_ms = value ? atol(value) : 0;
    }
    if (delay_ms > 0) {
        struct timespec ts = {delay_ms / 1000, (delay_ms % 1000) * 1000000L};
        nanosleep(&ts, NULL);
    }
}

int fsync(int fd) {
    static int (*real_fsync)(int) = NULL;
    if (!real_fsync) {
        real_fsync = dlsym(RTLD_NEXT, "fsync");
    }
    delay();
    return real_fsync(fd);
}

int fdatasync(int fd) {
    static int (*real_fdatasync)(int) = NULL;
    if (!real_fdatasync) {
        real_fdatasync = dlsym(RTLD_NEXT, "fdatasync");
    }
    delay();
    return real_fdatasync(fd);
}
