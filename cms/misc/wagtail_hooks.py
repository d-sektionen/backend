"""
In this file wagtail looks for hooks that can extend some funtionality.
https://docs.wagtail.io/en/v2.4/reference/hooks.html
"""

import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
from wagtail.core import hooks
from wagtail.admin.menu import MenuItem
from django.urls import reverse
from django.conf.urls import url

from . import views
from .gatsby import gatsby_manager

@hooks.register('register_rich_text_features')
def register_staben_text_feature(features):
    """
    Registering the `staben` feature, which uses the `STABEN` Draft.js inline style type,
    and is stored as HTML with an `<span>` tag.
    http://docs.wagtail.io/en/v2.4/advanced_topics/customisation/extending_draftail.html
    """
    feature_name = 'staben'
    type_ = 'STABEN'
    tag = 'span' # Yes, reserves span for STABEN text, should probably be improved.

    # Configure how Draftail handles the feature in its toolbar.
    control = {
        'type': type_,
        'icon': ["M761.6 361.8q-28.6-29.1-61.6-49.2t-68.5-36.3-72-30.2-72.3-31.1q-3.3-5.5-1.7-8.8t5-6.1 6.9-5.5 4.1-6.6q54.4 20.4 105.6 48.1t100.6 53.6q16.5-15.9 21.4-34.4t3.9-38.2-5-39.6-5.2-39.1 2.8-37.1 19.5-32.7q-5-5.5-8.2-13.5t-7.7-14.8-10.7-11.3-16.2-2.2q-28.6 5.5-57.7 5.8t-58.9-1.4-59.1-3.3-58.3.5-56.7 10.2-54.2 25.6q-6.1 16.5-17.3 29.2t-24.2 23.9-25.6 22.3-21.7 23.9-12.4 29.1 2.2 38.2q19.3 31.3 41.8 62.1t49.8 56.4 60.2 43.7 73.7 23.7q6.1 5.5 14.6 9.3t15.7 9.3 9.9 13.5-3.3 21.7q-18.7 5.5-35.5 1.9t-32.7-12.1-31.3-20.3-31.9-22-33.8-17.3-37.1-6.6q-11-3.3-24.5.6t-22.8 16.5q-1.6 22-2.5 41.3t-.8 37.4.3 36.3.3 39.1q5.5 15.4 18.4 25t28.3 16.5l30.8 13.8t26.4 16.8q22 11 34.4 27.2t19.5 35.5 10.7 40.1 7.4 41.3 9.6 38.8 17.3 32.7q6 0 9.9-1.6t8.3-3.3q-2.7-16-.5-31.4t4.9-31.6 4.4-33-2.2-35.5q6.6-7.1 11.6-13.7t9.6-11.8 10.7-9.6 15.4-6.6q1.1 17.6 6.9 34.7t13.2 33.8 14 34.1 8.8 36q-8.2 17.1-9.9 32.5t0 30.3 5.8 29.4 7.4 29.4 4.9 30.3-1.6 31.9h24.8q4.9-57.7 17-113t27.8-109.2 33.6-107.5 33.3-107.5q18.7-19.2 27.5-43.2t11.3-49.8 0-52.8-6.3-52.3z"],
        'description': 'STABEN text',
        # How the text is seen in the editor.
        'style': {'color': '#e63e32', 'font-family': 'ROCKYAOE', 'font-weight': 'normal'},
    }

    # Call register_editor_plugin to register the configuration for Draftail.
    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(control)
    )

    # Configure the content transform from the DB to the editor and back.
    db_conversion = {
        'from_database_format': {tag: InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: tag}},
    }

    # Call register_converter_rule to register the content transformation conversion.
    features.register_converter_rule('contentstate', feature_name, db_conversion)

@hooks.register('register_admin_urls')
def register_admin_urls():
    """
    Registers the url for gatsby builds.
    """
    return [
        url(r'^gatsby/$', views.gatsby, name='gatsby'),
    ]

@hooks.register('register_admin_menu_item')
def register_frank_menu_item():
    """
    Registers the menu for gatsby builds.
    """
    return MenuItem('Gatsby', reverse('gatsby'), classnames='icon icon-site', order=10000)


"""
Runs gatsby manager whenever a change is made to the content.
"""
@hooks.register('after_create_page')
def do_after_page_create(request, page):
    gatsby_manager(True)
@hooks.register('after_delete_page')
def do_after_page_delete(request, page):
    gatsby_manager(True)
@hooks.register('after_edit_page')
def do_after_page_edit(request, page):
    gatsby_manager(True)
@hooks.register('after_copy_page')
def do_after_page_copy(request, page):
    gatsby_manager(True)
@hooks.register('after_move_page')
def do_after_page_move(request, page):
    gatsby_manager(True)
