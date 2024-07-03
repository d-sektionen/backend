from .models import Entry


def log(description, category=Entry.UNCATEGORIZED, severity=Entry.INFO, user=None):
    obj = Entry.objects.create(
        description=description,
        category=category,
        severity=severity,
        user=user,
    )

    return obj is not None

