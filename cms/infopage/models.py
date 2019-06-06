"""
Wagtail Page model for informational pages, such as the pages about committees and general information about our section.
http://docs.wagtail.io/en/stable/topics/pages.html
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

class InfoPage(Page):
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    theme = models.ForeignKey(
        'snippets.Theme',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = StreamField([
        ('richtext', blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'bold', 'italic', 'staben', 'ol', 'ul', 'link'], )),
        ('social', SnippetChooserBlock(Committee)),
        ('contact', SnippetChooserBlock(Contact)),
        ('page', PageChooserBlock()),
    ])

    parent_page_types = ['InfoPage', 'home.HomePage']
    subpage_types = ['InfoPage']

    content_panels = Page.content_panels + [
        SnippetChooserPanel('theme'),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('body', classname="full"),
    ]

