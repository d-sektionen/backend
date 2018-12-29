"""
Contains implementation of streamfields for graphene (and some helper functions).
Based on: https://wagtail.io/blog/graphql-with-streamfield/
"""


import string

from wagtail.core.fields import StreamField
from graphene.types import Scalar

import graphene
from graphene.types.generic import GenericScalar
from graphene_django.converter import convert_django_field

from wagtail.images.models import Image
from graphene_django import DjangoObjectType

"""
Returns a tuple with a graphene Field and List for a graphene DjangoObjectType node.

nodeType is an object extending DjangoObjectType with a django model defined.
page should be set to True if the django model inherits from Page in order to only show published pages.
"""
def get_field_and_list_of_node_type(nodeType, page=False):
    # _meta is probably a private variable and can be changed in new releases.
    # An alternative is to use a second param in this function.
    model = nodeType._meta.model

    def resolve_multiple(self, info):
        return model.objects.live() if page else model.objects.all()
    def resolve_one(self, info, id):
        return model.objects.get(id=id)

    multiple = graphene.List(nodeType, resolver=resolve_multiple)
    one = graphene.Field(nodeType, id=graphene.ID(), resolver=resolve_one)

    return (one, multiple)



class GenericStreamFieldType(Scalar):
    @staticmethod
    def serialize(stream_value):
        return stream_value.stream_data


@convert_django_field.register(StreamField)
def convert_stream_field(field, registry=None):
    return GenericStreamFieldType(
        description=field.help_text, required=not field.null
    )


# We're creating a fallback / default ObjectType at this point
class DefaultStreamBlock(graphene.ObjectType):
    block_type = graphene.String()
    value = GenericScalar()

# This is our factory function
# Pass in kwargs with the block's name as the 
# keyword and the graphene type as its value
def create_stream_field_type(field_name, **kwargs):
    block_type_handlers = kwargs.copy()

    class Meta:
        types = (DefaultStreamBlock, ) + tuple(
            block_type_handlers.values())
    
    # This is where we generate the UnionType from the kwargs
    # Different graphene types can't have the same name, so we're
    # generating this class dynamically
    StreamFieldType = type(
        f"{string.capwords(field_name, sep='_').replace('_', '')}Type",
        (graphene.Union,),
        dict(Meta=Meta))

    def convert_block(block):
        block_type = block.get('type')
        value = block.get('value')
        if block_type in block_type_handlers:
            handler = block_type_handlers.get(block_type)
            if isinstance(value, dict):
                return handler(value=value, block_type=block_type, **value)
            else:
                return handler(value=value, block_type=block_type)
        else:
            return DefaultStreamBlock(value=value, block_type=block_type)

    # We also generate the resolver function for the field
    def resolve_field(self, info):
        field = getattr(self, field_name)
        return [convert_block(block) for block in field.stream_data]

    return (graphene.List(StreamFieldType), resolve_field)



class WagtailImageNode(DjangoObjectType):
    class Meta:
        model = Image
        # Tags would need a separate converter, so let's just
        # exclude it at this point to keep the scope smaller
        exclude_fields = ['tags']

@convert_django_field.register(Image)
def convert_image(field, registry=None):
    return WagtailImageNode(
        description=field.help_text, required=not field.null
    )