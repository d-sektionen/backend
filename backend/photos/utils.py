from uuid import uuid4


def get_photo_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"photoalbum/{instance.date.year}/{uuid4().hex}.{ext}"
