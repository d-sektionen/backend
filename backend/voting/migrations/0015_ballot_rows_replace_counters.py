import django.db.models.deletion
from django.db import migrations, models


def expand_counters_into_ballots(apps, schema_editor):
    """Keep historical tallies: one anonymous ballot row per counted vote."""
    Alternative = apps.get_model("voting", "Alternative")
    Ballot = apps.get_model("voting", "Ballot")
    db = schema_editor.connection.alias
    for alternative in (
        Alternative.objects.using(db).filter(num_votes__gt=0).iterator()
    ):
        Ballot.objects.using(db).bulk_create(
            [Ballot(alternative_id=alternative.pk) for _ in range(alternative.num_votes)],
            batch_size=500,
        )


def collapse_ballots_into_counters(apps, schema_editor):
    Alternative = apps.get_model("voting", "Alternative")
    db = schema_editor.connection.alias
    tallies = (
        Alternative.objects.using(db)
        .annotate(tally=models.Count("ballot"))
        .values_list("pk", "tally")
    )
    for pk, tally in tallies.iterator():
        Alternative.objects.using(db).filter(pk=pk).update(num_votes=tally)


class Migration(migrations.Migration):
    dependencies = [("voting", "0014_remove_redundant_receipt_index")]

    operations = [
        migrations.CreateModel(
            name="Ballot",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
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
        migrations.RunPython(
            expand_counters_into_ballots, collapse_ballots_into_counters
        ),
        migrations.RemoveField(model_name="alternative", name="num_votes"),
    ]
