"""
Contains wagtail snippets. Snippets are models editable in Wagtail that don't fit as Page models.
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
from django.contrib.auth.models import User
from .validators import color_lightness_validator

"""
Committee is for storing different committees (utskott).
Mostly for relations to other models such as Social Media.
"""
@register_snippet
class Committee(models.Model):
    name = models.CharField(max_length=255)

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

"""
A contact is for contact details of a position.
Contains which position, for example: "Secretary",
the corresponding email: "sekreterare@d-sektionen.se",
and the model of the user currently on the position.

Further details such as name and phone number should
if possible be retrieved from the user model.
"""
@register_snippet
class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    position = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    panels = [
        FieldPanel('position'),
        FieldPanel('email'),
        FieldPanel('user'),
    ]

    def __str__(self):
        return self.position

"""
A link to a social media profile that is linked to a committee.
Can be used to list all social media profiles of a specific committee.
"""
@register_snippet
class SocialMedia(models.Model):
    url = models.URLField(blank=True)
    text = models.CharField(max_length=255)
    committee = models.ForeignKey(
        'Committee',
        on_delete=models.CASCADE,
        related_name='+'
    )
    SOCIAL_MEDIA_TYPES = (
        ('F', 'Facebook'),
        ('I', 'Instagram'),
        ('G', 'GitHub'),
        ('O', 'Other')
    )
    network = models.CharField(max_length=1, choices=SOCIAL_MEDIA_TYPES, default='O')

    panels = [
        SnippetChooserPanel('committee'),
        FieldPanel('url'),
        FieldPanel('text'),
        FieldPanel('network')
    ]

    def __str__(self):
        return self.committee.name + ' - ' + self.text

"""
Details about a sponsor.
Made to show in the sidebar of the website.
"""
@register_snippet
class Sponsor(models.Model):
    url = models.URLField(null=True, blank=True)
    text = models.CharField(max_length=255)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    SPONSOR_PRIORITIES = (
        ('M', 'Main'),
        ('P', 'Partner'),
    )
    priority = models.CharField(max_length=1, choices=SPONSOR_PRIORITIES, default='P')

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('url'),
        FieldPanel('text'),
        FieldPanel('priority')
    ]

    def __str__(self):
        return self.text

"""
Theme is a model for customizing the look of a page.
Can for example be used to give the Donna page a pink background.
"""
@register_snippet
class Theme(models.Model):
    name = models.CharField(max_length=255)
    background_color = models.CharField(max_length=6, validators=[color_lightness_validator(242)])
    panel_color = models.CharField(max_length=6, validators=[color_lightness_validator(230)])
    
    panels = [
        FieldPanel('name'),
        FieldPanel('background_color'),
        FieldPanel('panel_color')
    ]

    def __str__(self):
        return self.name