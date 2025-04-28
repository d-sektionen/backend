def get_photo_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"photoalbum/{instance.date.year}/{instance.title}.{ext}"
