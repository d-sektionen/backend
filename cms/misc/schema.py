import graphene
from graphene_django import DjangoObjectType
from wagtail.core.models import Page
from django.contrib.auth.models import User
from wagtail.contrib.redirects.models import Redirect

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

class UserNode(DjangoObjectType):
  class Meta:
    model = User
    only_fields = ['display_name', 'contact_set', 'id']

  display_name = graphene.String()

  def resolve_display_name(self, info):
    return self.get_full_name() or self.get_username()

class RedirectNode(DjangoObjectType):
  class Meta:
    model = Redirect