"""Load-test vote casting against a running backend.

Seeds a meeting with attending student members and one open ballot, casts one
vote per member over HTTP with a fixed number of concurrent requests, and
reports latency and throughput. The seeded data is deleted afterwards.

    python manage.py bench_voting --url http://localhost:8000 --voters 200 --concurrency 50

Run it inside the backend container of compose.bench.yml to include a slow
disk; see benchmark/README.md.
"""

import json
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from unittest.mock import patch

import requests
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework_simplejwt.tokens import AccessToken

from backend.membership.models import Member
from backend.voting.models import Alternative, Attendant, Meeting, Vote

PREFIX = "bn"  # + 6 digits fits the 8-character liu_id
NAME = "Benchmark voting"


class Command(BaseCommand):
    help = "Cast many concurrent votes against a running backend and report timings"

    def add_arguments(self, parser):
        parser.add_argument("--url", default="http://localhost:8000")
        parser.add_argument("--voters", type=int, default=200)
        parser.add_argument("--concurrency", type=int, default=50)
        parser.add_argument("--alternatives", type=int, default=3)
        parser.add_argument(
            "--first-share",
            type=float,
            default=0.7,
            help="Share of voters picking the first alternative; the rest spread evenly",
        )
        parser.add_argument(
            "--rounds", type=int, default=1, help="Repeat with a fresh ballot"
        )
        parser.add_argument("--label", default="", help="Tag for the JSON summary")

    def handle(self, *args, **options):
        # Socket notifications are published by the HTTP workers that accept
        # the votes. This command is not a socket server, and emit_event cannot
        # be called repeatedly from a plain sync process, so mute it here.
        with patch("backend.voting.signals.emit_event"):
            self.cleanup()
            meeting = Meeting.objects.create(name=NAME, clear_data=date.today())
            try:
                users = self.seed_voters(meeting, options["voters"])
                tokens = {user.pk: str(AccessToken.for_user(user)) for user in users}
                for round_number in range(1, options["rounds"] + 1):
                    vote = Vote.objects.create(
                        meeting=meeting, question=f"Round {round_number}"
                    )
                    alternatives = Alternative.objects.bulk_create(
                        [
                            Alternative(vote=vote, text=f"Alternative {i}")
                            for i in range(options["alternatives"])
                        ]
                    )
                    self.run_round(
                        round_number, vote, alternatives, users, tokens, options
                    )
            finally:
                self.cleanup()

    def cleanup(self):
        """Remove seeded data, including leftovers from an interrupted run."""
        Meeting.objects.filter(name=NAME).delete()
        User.objects.filter(username__regex=rf"^{PREFIX}\d{{6}}$").delete()
        Member.objects.filter(liu_id__regex=rf"^{PREFIX}\d{{6}}$").delete()

    def seed_voters(self, meeting, count):
        users = User.objects.bulk_create(
            [User(username=f"{PREFIX}{i:06d}") for i in range(count)]
        )
        Member.objects.bulk_create(
            [Member(liu_id=user.username, membership_type="S") for user in users]
        )
        Attendant.objects.bulk_create(
            [Attendant(user=user, meeting=meeting) for user in users]
        )
        return users

    def run_round(self, round_number, vote, alternatives, users, tokens, options):
        first = int(len(users) * options["first_share"])
        others = alternatives[1:] or alternatives
        choices = [
            alternatives[0] if i < first else others[i % len(others)]
            for i in range(len(users))
        ]
        local = threading.local()
        url = options["url"].rstrip("/") + "/voting/made_votes/"

        def cast(index):
            session = getattr(local, "session", None)
            if session is None:
                session = local.session = requests.Session()
            user = users[index]
            started = time.perf_counter()
            try:
                response = session.post(
                    url,
                    json={"vote_id": vote.pk, "alternative_id": choices[index].pk},
                    cookies={"access_token": tokens[user.pk]},
                    timeout=120,
                )
                status = response.status_code
            except requests.RequestException as error:
                status = type(error).__name__
            return status, time.perf_counter() - started

        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=options["concurrency"]) as pool:
            results = list(pool.map(cast, range(len(users))))
        elapsed = time.perf_counter() - started

        latencies = sorted(seconds for _, seconds in results)
        statuses = {}
        for status, _ in results:
            statuses[str(status)] = statuses.get(str(status), 0) + 1

        def percentile(share):
            return latencies[min(len(latencies) - 1, int(share * len(latencies)))]

        summary = {
            "label": options["label"],
            "round": round_number,
            "voters": len(users),
            "concurrency": options["concurrency"],
            "statuses": statuses,
            "wall_seconds": round(elapsed, 3),
            "votes_per_second": round(len(users) / elapsed, 1),
            "latency_ms": {
                "p50": round(1000 * statistics.median(latencies), 1),
                "p90": round(1000 * percentile(0.9), 1),
                "p99": round(1000 * percentile(0.99), 1),
                "max": round(1000 * latencies[-1], 1),
            },
        }
        self.stdout.write(
            f"round {round_number}: {len(users)} votes, {options['concurrency']} concurrent, "
            f"{elapsed:.2f} s wall, {summary['votes_per_second']} votes/s, "
            f"p50 {summary['latency_ms']['p50']} ms, p99 {summary['latency_ms']['p99']} ms, "
            f"max {summary['latency_ms']['max']} ms, statuses {statuses}"
        )
        self.stdout.write(json.dumps(summary))
