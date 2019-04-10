import graphene
from graphene_django import DjangoObjectType
from .models import Committee, Contact,SocialMedia,Sponsor,Theme
from cms.misc.schema import PageInterface, UserNode

class SocialMediaNode(DjangoObjectType):
  class Meta:
    model = SocialMedia

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