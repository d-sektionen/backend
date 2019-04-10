import graphene
from graphene_django import DjangoObjectType
from .models import InfoPage
from cms.misc.schema import PageInterface
from cms.graphql.blocks import body_field

class InfoPageNode(DjangoObjectType):
  (body, resolve_body) = body_field

  class Meta:
    model = InfoPage
    only_fields = []
    interfaces = (PageInterface,)