import graphene
from graphene_django import DjangoObjectType
from .models import Post, PostIndex
from cms.misc.schema import PageInterface
from cms.graphql.blocks import body_field

class PostNode(DjangoObjectType):
  (body, resolve_body) = body_field

  class Meta:
    model = Post
    only_fields = []
    interfaces = (PageInterface,)

class PostIndexNode(DjangoObjectType):
  class Meta:
    model = PostIndex
    only_fields = []
    interfaces = (PageInterface,)

  posts = graphene.List(PostNode)

  def resolve_posts(self, info):
    return Post.objects.child_of(self).live()