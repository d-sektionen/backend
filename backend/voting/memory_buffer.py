"""Experimental shared in-memory vote buffer; a Redis restart requires a revote.

Use a dedicated Redis instance with persistence disabled. Voter IDs and choice
counts occupy separate fields: no stored field associates a voter with a choice.
"""

from functools import lru_cache

import redis
from django.conf import settings
from rest_framework.exceptions import APIException


class BufferUnavailable(APIException):
    status_code = 503
    default_detail = "Voting buffer unavailable or lost; start a new ballot and revote."


@lru_cache(maxsize=1)
def client():
    return redis.Redis.from_url(settings.VOTING_BUFFER_REDIS_URL, decode_responses=True,
                                socket_connect_timeout=2, socket_timeout=2)


def key(vote_id):
    return f"voting:experimental:{vote_id}"


def call(method, *args, **kwargs):
    try:
        return getattr(client(), method)(*args, **kwargs)
    except redis.RedisError as error:
        raise BufferUnavailable() from error


def initialize(vote_id):
    if not call("hsetnx", key(vote_id), "state", "open"):
        raise BufferUnavailable("Voting buffer already exists; create a new ballot.")


CAST = """
local state = redis.call('HGET', KEYS[1], 'state')
if not state then return -1 end
if state ~= 'open' then return -2 end
if redis.call('HEXISTS', KEYS[1], 'v:' .. ARGV[1]) == 1 then return 0 end
redis.call('HSET', KEYS[1], 'v:' .. ARGV[1], '1')
redis.call('HINCRBY', KEYS[1], 'c:' .. ARGV[2], 1)
return 1
"""


def cast(vote_id, user_id, alternative_id):
    result = call("eval", CAST, 1, key(vote_id), user_id, alternative_id)
    if result < 0:
        raise BufferUnavailable()
    return result == 1


def snapshot(vote_id):
    values = call("hgetall", key(vote_id))
    if values.get("state") not in ("open", "closing"):
        raise BufferUnavailable()
    voters = [int(k[2:]) for k in values if k.startswith("v:")]
    counts = {int(k[2:]): int(v) for k, v in values.items() if k.startswith("c:")}
    return voters, counts


def has_voted(vote_id, user_id):
    values = call("hmget", key(vote_id), ["state", f"v:{user_id}"])
    if values[0] not in ("open", "closing"):
        raise BufferUnavailable()
    return values[1] is not None


def freeze(vote_id):
    result = call("eval", """
        local state = redis.call('HGET', KEYS[1], 'state')
        if state == 'closing' then return 1 end
        if state ~= 'open' then return 0 end
        redis.call('HSET', KEYS[1], 'state', 'closing')
        return 1
    """, 1, key(vote_id))
    if not result:
        raise BufferUnavailable()


def discard(vote_id):
    # The PostgreSQL transaction is already committed when this runs.
    # Redis may be unavailable; closed ballots remain readable from PostgreSQL.
    try:
        call("delete", key(vote_id))
    except BufferUnavailable:
        pass
