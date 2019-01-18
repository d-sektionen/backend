"""
Contains the GraphQL (using graphene) schema definition.

Which schema to use is described in the django app settings.

The GraphQL api should be seen as an alternative to the REST API.
At the moment this API only allows retrieving data.
"""

from __future__ import unicode_literals
import graphene
from graphene_django import DjangoObjectType
from cms.infopage.models import InfoPage

from wagtail.core.models import Page

from django.db import models
from django.contrib.auth.models import User

from .graphene_wagtail import DefaultStreamBlock, create_stream_field_type
from cms.infopage.models import InfoPage
from cms.snippets.models import Committee, Sponsor, SocialMedia, Contact, Theme
from cms.home.models import HomePage
from cms.infomail.models import InfomailIndexPage, InfomailPage, InfomailArticlePage
from wagtail.contrib.redirects.models import Redirect
from graphene.types.generic import GenericScalar

from .graphene_wagtail import get_field_and_list_of_node_type

class PageInterface(graphene.Interface):
  url = graphene.String()
  type = graphene.String()
  slug = graphene.String()
  id = graphene.ID(required=True)
  title = graphene.String(required=True)
  show_in_menus = graphene.Boolean()

  def resolve_url(self, info):
    return '/' + ('/'.join(map(lambda x: x.slug, list(self.get_ancestors(True))[2:])))

class PageNode(DjangoObjectType):
  class Meta:
    model = Page
    only_fields = []
    interfaces = (PageInterface,)

class SocialMediaNode(DjangoObjectType):
  class Meta:
    model = SocialMedia

class UserNode(DjangoObjectType):
  class Meta:
    model = User
    only_fields = ['display_name', 'contact_set', 'id']

  display_name = graphene.String()

  def resolve_display_name(self, info):
    return self.get_full_name() or self.get_username()

class ContactNode(DjangoObjectType):
  class Meta:
    model = Contact

  user = graphene.Field(UserNode)

  def resolve_user(self, info):
    return self.user

class CommitteeNode(DjangoObjectType):
  social_medias = graphene.List(SocialMediaNode)
  class Meta:
    model = Committee

  def resolve_social_medias(self, info):
    return SocialMedia.objects.filter(committee=self)

class SponsorNode(DjangoObjectType):
  class Meta:
    model = Sponsor

class ThemeNode(DjangoObjectType):
  class Meta:
    model = Theme

class RichtextBlock(DefaultStreamBlock):
  pass

class MarkdownBlock(DefaultStreamBlock):
  pass

class ContactBlock(DefaultStreamBlock):
  contact = graphene.Field(ContactNode)

  def resolve_contact(self, info):
    return Contact.objects.get(id=self.value)

class SocialBlock(DefaultStreamBlock):
  committee = graphene.Field(CommitteeNode)

  def resolve_committee(self, info):
    return Committee.objects.get(id=self.value)

class PageBlock(DefaultStreamBlock):
  page = graphene.Field(PageNode)

  def resolve_page(self, info):
    return Page.objects.get(id=self.value)


class InfoPageNode(DjangoObjectType):
  (body, resolve_body) = create_stream_field_type(
        'body',
        richtext=RichtextBlock,
        markdown=MarkdownBlock, 
        social=SocialBlock,
        page=PageBlock,
        contact=ContactBlock)

  class Meta:
    model = InfoPage
    only_fields = []
    interfaces = (PageInterface,)

class HomePageNode(DjangoObjectType):
  class Meta:
    model = HomePage
    only_fields = []
    interfaces = (PageInterface,)

class InfomailArticlePageNode(DjangoObjectType):
  class Meta:
    model = InfomailArticlePage
    only_fields = []
    interfaces = (PageInterface,)

class InfomailPageNode(DjangoObjectType):
  class Meta:
    model = InfomailPage
    only_fields = []
    interfaces = (PageInterface,)
  
  articles = graphene.List(InfomailArticlePageNode)

  def resolve_articles(self, info):
    return InfomailArticlePage.objects.child_of(self).live()

class InfomailIndexPageNode(DjangoObjectType):
  class Meta:
    model = InfomailIndexPage
    only_fields = []
    interfaces = (PageInterface,)

  infomail_pages = graphene.List(InfomailPageNode)

  def resolve_infomail_pages(self, info):
    return InfomailPage.objects.child_of(self).live()

class RedirectNode(DjangoObjectType):
  class Meta:
    model = Redirect

"""
The main query of the graphql endpoint, includes all exposed types.
"""
class Query(graphene.ObjectType):
  # ---
  # Pages
  # ---

  # General pages, includes limited information for all Page types.
  (page, pages) = get_field_and_list_of_node_type(PageNode, page=True)

  (info_page, info_pages) = get_field_and_list_of_node_type(InfoPageNode, page=True)

  (home_page, home_pages) = get_field_and_list_of_node_type(HomePageNode, page=True)

  (infomail_index_page, infomail_index_pages) = get_field_and_list_of_node_type(InfomailIndexPageNode, page=True)
  (infomail_page, infomail_pages) = get_field_and_list_of_node_type(InfomailPageNode, page=True)

  # ---
  # Snippets
  # ---

  (committee, committees) = get_field_and_list_of_node_type(CommitteeNode)
  (contact, contacts) = get_field_and_list_of_node_type(ContactNode)
  (sponsor, sponsors) = get_field_and_list_of_node_type(SponsorNode)

  # ---
  # Other
  # ---

  # Redirects (settings)
  (redirect, redirects) = get_field_and_list_of_node_type(RedirectNode)

schema = graphene.Schema(query=Query)