from django.conf import settings
from django.contrib.auth.models import User

from membership.utils import check_membership, get_name
from .models import Section

"""
Contains the callback used by the CAS plugin. This callback is called
for every login, before the corresponding user has been created. It cannot
be assumed that the user exist in these callbacks. Also note that the incoming
tree object may be modified in place, but only contains one thing: the username
accessed at tree[0][0].text.
"""
def cas_callback(tree):
    # Normalize the username to lower-case letters.
    # This ensures that a single student only has one Django account,
    # regardless of how the student input their username in CAS.
    username = tree[0][0].text.lower()

    user, created = get_or_create_user(username)

    # Set email on all cas logins if email is not set to something else.
    if not len(user.email):
        user.email = username + '@student.liu.se'
        user.save()

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
Sets a user to admin if declared as such in django settings.
"""
def apply_admin_permissions(user):
    if user.username in settings.SYSTEM_ADMINS:
        user.is_staff = True
        user.is_superuser = True
        user.save()

"""
Adds a user to the "D-sektionen" group if their username is a liu_id in the membership database.
"""
def add_to_section_groups(user):
    section = Section.objects.get(name="D-sektionen")
    if section and check_membership(user.username):
        group = section.user_group
        user.groups.add(group)


"""
Creates a user with the given username (usually liu_id)
The user gets privileges and their name set.
"""
def get_or_create_user(username):
    # "if student" must've gone somewhere
    user, created = User.objects.get_or_create(username=username)

    apply_admin_permissions(user)
    add_to_section_groups(user)
    set_name(user)
    if created:
        print('Created non-existing user')

    return user, created
