import uuid

import django.db.models.deletion
from django.db import migrations, models


def copy_ballots(apps, schema_editor, source, target):
    Source = apps.get_model("voting", source)
    Target = apps.get_model("voting", target)
    db = schema_editor.connection.alias
    batch = []
    for alternative_id in (
        Source.objects.using(db)
        .values_list("alternative_id", flat=True)
        .iterator(chunk_size=500)
    ):
        batch.append(Target(alternative_id=alternative_id))
        if len(batch) == 500:
            Target.objects.using(db).bulk_create(batch)
            batch.clear()
    Target.objects.using(db).bulk_create(batch)


def forwards(apps, schema_editor):
    copy_ballots(apps, schema_editor, "Ballot", "RandomBallot")


def backwards(apps, schema_editor):
    copy_ballots(apps, schema_editor, "RandomBallot", "Ballot")


class Migration(migrations.Migration):
    dependencies = [("voting", "0015_ballot_rows_replace_counters")]

    operations = [
        migrations.CreateModel(
            name="RandomBallot",
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
                    "alternative",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="voting.alternative",
                    ),
                ),
            ],
        ),
        migrations.RunPython(forwards, backwards),
        migrations.DeleteModel(name="Ballot"),
        migrations.RenameModel(old_name="RandomBallot", new_name="Ballot"),
    ]
