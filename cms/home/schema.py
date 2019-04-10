import graphene
from graphene_django import DjangoObjectType
from .models import HomePage
from cms.misc.schema import PageInterface

class HomePageNode(DjangoObjectType):
  class Meta:
    model = HomePage
    only_fields = []
    interfaces = (PageInterface,)