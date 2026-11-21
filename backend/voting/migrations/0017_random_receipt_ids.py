import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def copy_receipts(apps, schema_editor, source, target):
    Source = apps.get_model("voting", source)
    Target = apps.get_model("voting", target)
    db = schema_editor.connection.alias
    batch = []
    rows = Source.objects.using(db).values_list("user_id", "vote_id")
    for user_id, vote_id in rows.iterator(chunk_size=500):
        batch.append(Target(user_id=user_id, vote_id=vote_id))
        if len(batch) == 500:
            Target.objects.using(db).bulk_create(batch)
            batch.clear()
    Target.objects.using(db).bulk_create(batch)


def forwards(apps, schema_editor):
    copy_receipts(apps, schema_editor, "MadeVote", "RandomReceipt")


def backwards(apps, schema_editor):
    copy_receipts(apps, schema_editor, "RandomReceipt", "MadeVote")


class Migration(migrations.Migration):
    dependencies = [
        ("voting", "0016_random_ballot_ids"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RandomReceipt",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_index=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vote",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="voting.vote"
                    ),
                ),
            ],
        ),
        migrations.RunPython(forwards, backwards),
        migrations.DeleteModel(name="MadeVote"),
        migrations.RenameModel(old_name="RandomReceipt", new_name="MadeVote"),
        migrations.AddConstraint(
            model_name="madevote",
            constraint=models.UniqueConstraint(
                fields=("user", "vote"), name="one_vote_per_user"
            ),
        ),
    ]
