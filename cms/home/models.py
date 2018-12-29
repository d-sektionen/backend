"""
Wagtail Page for the homepage.
http://docs.wagtail.io/en/stable/topics/pages.html
"""

from django.db import models

from wagtail.core.models import Page
from wagtail.api import APIField


class HomePage(Page):
    parent_page_types = ['wagtailcore.Page']
    
    @classmethod
    def can_create_at(cls, parent):
        # You can only create one of these!
        return super(HomePage, cls).can_create_at(parent) \
            and not cls.objects.exists()

    def url(self):
        return '/' + ('/'.join(map(lambda x: x.slug, list(self.get_ancestors(True))[2:])))

    api_fields = [
        APIField('url')
    ]
