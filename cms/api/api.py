"""
Contains a Django REST Framework based api definition for the CMS.

At the moment this API only allows retrieving data.

All of the base api endpoints from wagtail have been extened to better fit our needs.
Basic documentation: http://docs.wagtail.io/en/stable/advanced_topics/api/index.html
"""

from django.db.models import Model
from wagtail.api.v2.views import PagesAPIViewSet, BaseAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.serializers import PageSerializer
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet
from rest_framework.fields import Field
from rest_framework.permissions import AllowAny
from wagtail.core.models import Page


class PageUrlField(Field):
    """
    Serializes the "url" field for pages.
    Example:
    "url": "/blog/blog-post/"
    """
    def get_attribute(self, instance):
        return instance

    def to_representation(self, page):
        return '/' + ('/'.join(map(lambda x: x.slug, list(page.get_ancestors(True))[2:])))

class ExtendedPageSerializer(PageSerializer):
    url = PageUrlField(read_only=True)

# Extend PagesAPIViewSet
class ExtendedPagesAPIViewSet(PagesAPIViewSet):
    model = Page
    base_serializer_class = ExtendedPageSerializer
    authentication_classes = []
    permission_classes = (AllowAny,)
    meta_fields = PagesAPIViewSet.meta_fields + [
       'url'
    ]

class ExtendedImagesAPIViewSet(ImagesAPIViewSet):
    authentication_classes = []
    permission_classes = (AllowAny,)

class ExtendedDocumentsAPIViewSet(DocumentsAPIViewSet):
    authentication_classes = []
    permission_classes = (AllowAny,)

# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')

# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint('pages', ExtendedPagesAPIViewSet)
api_router.register_endpoint('images', ExtendedImagesAPIViewSet)
api_router.register_endpoint('documents', ExtendedDocumentsAPIViewSet)
# api_router.register_endpoint('snippets', SnippetAPIViewSet) // a custom snippet endpoint can be created by extending BaseAPIViewSet
