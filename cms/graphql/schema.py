"""
Contains the GraphQL (using graphene) schema definition.

Which schema to use is described in the django app settings.

The GraphQL api should be seen as an alternative to the REST API.
At the moment this API only allows retrieving data.
"""

from __future__ import unicode_literals
import graphene
from graphene_django import DjangoObjectType
from graphene.types.generic import GenericScalar
from .graphene_wagtail import get_field_and_list_of_node_type

from cms.infomail.schema import InfomailArticlePageNode, InfomailIndexPageNode, InfomailPageNode
from cms.home.schema import HomePageNode
from cms.infopage.schema import InfoPageNode
from cms.snippets.schema import CommitteeNode, ContactNode, SocialMediaNode, SponsorNode
from cms.misc.schema import PageNode, RedirectNode
from cms.post.schema import PostNode, PostIndexNode

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

  (post_index, post_indexes) = get_field_and_list_of_node_type(PostIndexNode, page=True)
  (post, posts) = get_field_and_list_of_node_type(PostNode, page=True)

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