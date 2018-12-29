"""
Wagtail Page models for infomail related pages.
http://docs.wagtail.io/en/stable/topics/pages.html
"""

from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.api.fields import ImageRenditionField
from wagtail.api import APIField

from cms.infopage.models import InfoPage

# Parent of InfomailPages.
class InfomailIndexPage(Page):
    description = RichTextField(blank=False, null=False, features=['h2', 'h3', 'h4', 'bold', 'italic', 'staben', 'ol', 'ul', 'link'])

    parent_page_types = ['home.HomePage']
    subpage_types = ['InfomailPage']

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full")
    ]

# An InfomailPage contains the data is sent out by a single email. It has InfomailArticlePages as children.
class InfomailPage(Page):
    intro = RichTextField(blank=True, features=['bold', 'italic', 'ol', 'ul', 'link'], help_text='Intro is an optional full-width container shown on top of the email under the logo.')
    intro_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    intro_image_text = RichTextField(blank=True, features=['bold', 'italic', 'ol', 'ul', 'link'], help_text='The image text is shown underneath the intro image and describes the image.')
    intro_image_link = models.URLField(null=True, blank=True)

    parent_page_types = ['InfomailIndexPage']
    subpage_types = ['InfomailArticlePage']

    api_fields = [
        APIField('intro'),
        APIField('intro_image'),
        APIField('intro_image_optimized', serializer=ImageRenditionField('width-780', source='image')),
        APIField('intro_image_text'),
        APIField('intro_image_link'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        MultiFieldPanel(heading="Intro Image", children = [
            FieldRowPanel([
                ImageChooserPanel('intro_image'),
                FieldPanel('intro_image_link'),
            ]),
            FieldPanel('intro_image_text'),
        ]),
    ]

# Stores a single article from an infomail.
class InfomailArticlePage(Page):
    description = RichTextField(blank=False, null=False, features=['h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'link'])
    link = models.URLField(null=True, blank=True)
    link_text = models.CharField(max_length=63, blank=True, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    image_link = models.URLField(null=True, blank=True)

    parent_page_types = ['InfomailPage']
    subpage_types = []

    api_fields = [
        APIField('description'),
        APIField('link'),
        APIField('link_text'),
        APIField('image'),
        APIField('image_optimized', serializer=ImageRenditionField('width-500', source='image')),
        APIField('image_link'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full"),
        MultiFieldPanel(heading="Read more link", children=[
            FieldRowPanel([
                FieldPanel('link'),
                FieldPanel('link_text')
            ]),
        ]),
        MultiFieldPanel(heading="Image", children=[
            FieldRowPanel([
                ImageChooserPanel('image'),
                FieldPanel('image_link')
            ])
        ])
    ]