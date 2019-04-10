import graphene
from .graphene_wagtail import DefaultStreamBlock, create_stream_field_type
from cms.snippets.schema import ContactNode, CommitteeNode
from cms.snippets.models import Contact, Committee
from wagtail.core.models import Page
from cms.misc.schema import PageNode

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

body_field = create_stream_field_type(
        'body',
        richtext=RichtextBlock,
        markdown=MarkdownBlock, 
        social=SocialBlock,
        page=PageBlock,
        contact=ContactBlock)