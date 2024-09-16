from django.contrib.auth.models import User

from membership.utils import get_name

"""
Sets the name of a user based on data in the Membership database.
Will only be set if not previously set.
"""


def set_name(user):
    if not (len(user.first_name) or len(user.last_name)):
        first, last = get_name(user.username)

        if first is not None:
            user.first_name = first
            user.last_name = last
            user.save()


"""
Creates a user with the given username (usually liu_id)
The user gets privileges and their name set.
"""


def get_or_create_user(username):
    # "if student" must've gone somewhere
    user, created = User.objects.get_or_create(username=username)

    set_name(user)

    return user, created
