from django.db import migrations, models


def reject_duplicate_receipts(apps, schema_editor):
    receipts = apps.get_model("voting", "MadeVote")
    duplicates = (
        receipts.objects.using(schema_editor.connection.alias)
        .values("user_id", "vote_id")
        .annotate(total=models.Count("id"))
        .filter(total__gt=1)
    )
    if duplicates.exists():
        raise RuntimeError(
            "Duplicate voting receipts exist. Stop voting and audit affected ballots "
            "before retrying this migration. Anonymous tallies cannot safely be "
            "repaired by deleting receipts."
        )


class Migration(migrations.Migration):
    dependencies = [("voting", "0012_auto_20240524_2224")]
    operations = [
        migrations.RunPython(reject_duplicate_receipts, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="madevote",
            constraint=models.UniqueConstraint(
                fields=("user", "vote"), name="one_vote_per_user"
            ),
        ),
    ]
