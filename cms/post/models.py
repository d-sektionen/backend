"""
Wagtail Page models for blog posts (aka news)
"""

from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.models import Image
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.core.blocks import PageChooserBlock
from cms.snippets.models import Contact, Committee

class PostIndex(Page):
  parent_page_types = ['home.HomePage']
  subpage_types = ['Post']

class Post(Page):
    body = StreamField([
        ('richtext', blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'bold', 'italic', 'staben', 'ol', 'ul', 'link'], )),
        ('social', SnippetChooserBlock(Committee)),
        ('contact', SnippetChooserBlock(Contact)),
        ('page', PageChooserBlock()),
    ])

    parent_page_types = ['PostIndex']
    subpage_types = []

    content_panels = Page.content_panels + [
        StreamFieldPanel('body', classname="full")
    ]

