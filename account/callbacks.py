"""
Contains all the callbacks used by the CAS plugin. These callbacks are called
for every login, before the corresponding user has been created. It cannot
be assumed that the user exist in these callbacks. Also note that the incoming
tree object may be modified in place, but only contains one thing: the username
accessed at tree[0][0].text.
"""


from django.conf import settings
from django.contrib.auth.models import User, Group

from account.section_membership import check_membership
from voting.models import Section


def normalize_username(tree):
    """
    Makes sure that the username consist of only lower-case letters. This
    ensures that a single student only has one Django account, regardless
    of how the student input their username in CAS.
    """

    tree[0][0].text = tree[0][0].text.lower()


def apply_admin_permissions(tree):
    """
    Temporary callback to make configured users able to access the Django
    admin pages. To configure the users, see ADMINS in "app/settings_shared.py"
    """

    user, user_created = _get_or_create_user(tree)

    if user.username in settings.ADMINS:
        user.is_staff = True
        user.is_superuser = True
        user.save()


def add_to_section_groups(tree):
    """
    Checks program membership and adds the user to the section groups in which
    they belong.
    """

    user, user_created = _get_or_create_user(tree)
    sections = Section.objects.all()
    for section in sections:
        is_member = check_membership(user.username, section)
        if is_member:
            group, created = Group.objects.get_or_create(name=section.name)
            user.groups.add(group)


def _get_or_create_user(tree):
    """
    Creates the corresponding Django account for the given tree if it's
    not created, then returns the already existing or just created account.
    """

    username = tree[0][0].text
    return User.objects.get_or_create(username=username)

