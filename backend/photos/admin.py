from django.contrib import admin
from .models import Photo, PhotoAlbum, PhotoTag


class PhotoTagAdmin(admin.ModelAdmin):
    pass

class PhotoAlbumAdmin(admin.ModelAdmin):
    pass

class PhotoAdmin(admin.ModelAdmin):
    pass


admin.site.register(PhotoTag, PhotoTagAdmin)
admin.site.register(PhotoAlbum, PhotoAlbumAdmin)
admin.site.register(Photo, PhotoAdmin)
