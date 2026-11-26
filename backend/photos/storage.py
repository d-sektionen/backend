from django.core.files.storage import FileSystemStorage
from django.conf import settings

protected_storage = FileSystemStorage(
    location=settings.PROTECTED_MEDIA_ROOT,
    # we don't use generated image URLs in favor of the download view on the photo viewset
    # the base_url=None operation is a no-op, but kept to explicitly mark it as unused
    base_url=None,
)
