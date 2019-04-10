import graphene
from graphene_django import DjangoObjectType
from .models import InfomailArticlePage, InfomailIndexPage, InfomailPage
from cms.misc.schema import PageInterface

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