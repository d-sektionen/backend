# CMS

This is the CMS part of the website, to be used for the informational part of our website.

It is based on Wagtail for the admin interface, but doesn't use templates.
Instead the aim is to use it headless, as a REST or GraphQL API.

Although it is designed to be used by a frontend made in GatsbyJS,
it should be flexible enough to be useful in other frontends.

## Before you start

When working with this part of the project the most important prerequisite is to be familiar with Django principles as Wagtail is based on it.
Other than that it is good to have a grasp of how Wagtail and Graphene work, and to a lesser extent Django REST Framework.

## TODO

### Important

- Documentation.
- Complete to do list.
- Finish the post type.
- Add a translation implementation. Should be well thought out.
- Add descriptions in the admin interface.
- Move graphql schemas to their respective models.
- Tool for migrating from Wordpress.
- Fix TODO comments.

### Less important

- General code clean up.
- Search backend.
- I have heard tests are cool.

### Done

- Basic structure.
- Add GraphQL support.
