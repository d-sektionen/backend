from datetime import date
from unittest import skipUnless

from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


@skipUnless(connection.vendor == "postgresql", "Verifies PostgreSQL schema and indexes")
class ReceiptMigrationTests(TransactionTestCase):
    old = [("voting", "0012_auto_20240524_2224")]
    new = [("voting", "0017_random_receipt_ids")]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.old)
        apps = executor.loader.project_state(self.old).apps
        self.Receipt = apps.get_model("voting", "MadeVote")
        self.Alternative = apps.get_model("voting", "Alternative")
        self.Vote = apps.get_model("voting", "Vote")
        user = apps.get_model("auth", "User").objects.create(username="migrate1")
        meeting = apps.get_model("voting", "Meeting").objects.create(
            name="Migration", clear_data=date.today()
        )
        self.vote = self.Vote.objects.create(meeting=meeting, question="History")
        self.choice = self.Alternative.objects.create(
            vote=self.vote, text="Anonymous", num_votes=1
        )
        self.receipt = self.Receipt.objects.create(user=user, vote=self.vote)
        self.addCleanup(self.restore_schema)

    def restore_schema(self):
        # Discard the entire invalid synthetic ballot; never infer a choice from
        # a duplicate receipt or implement historical tally repair.
        self.Vote.objects.all().delete()
        MigrationExecutor(connection).migrate(self.new)

    def test_duplicate_preflight_preserves_all_anonymous_evidence(self):
        self.Receipt.objects.create(user_id=self.receipt.user_id, vote=self.vote)
        self.Alternative.objects.filter(pk=self.choice.pk).update(num_votes=2)
        with self.assertRaisesRegex(RuntimeError, "Duplicate voting receipts exist"):
            MigrationExecutor(connection).migrate(self.new)
        self.assertEqual(self.Receipt.objects.count(), 2)
        self.assertEqual(self.Alternative.objects.get(pk=self.choice.pk).num_votes, 2)

    def test_upgrade_and_rollback_preserve_tally_and_index_coverage(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.new)
        Ballot = executor.loader.project_state(self.new).apps.get_model(
            "voting", "Ballot"
        )
        self.assertEqual(
            Ballot.objects.filter(alternative_id=self.choice.pk).count(), 1
        )
        with connection.cursor() as cursor:
            indexes = connection.introspection.get_constraints(
                cursor, "voting_madevote"
            )
        self.assertEqual(
            indexes["one_vote_per_user"]["columns"], ["user_id", "vote_id"]
        )
        self.assertTrue(indexes["one_vote_per_user"]["unique"])
        self.assertFalse(
            any(i["columns"] == ["user_id"] and i["index"] for i in indexes.values())
        )
        self.assertTrue(
            any(i["columns"] == ["vote_id"] and i["index"] for i in indexes.values())
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.Receipt.objects.create(user_id=self.receipt.user_id, vote=self.vote)
        MigrationExecutor(connection).migrate(self.old)
        self.assertEqual(self.Receipt.objects.count(), 1)
        self.assertEqual(self.Alternative.objects.get(pk=self.choice.pk).num_votes, 1)
        with connection.cursor() as cursor:
            indexes = connection.introspection.get_constraints(
                cursor, "voting_madevote"
            )
        self.assertTrue(
            any(i["columns"] == ["user_id"] and i["index"] for i in indexes.values())
        )
