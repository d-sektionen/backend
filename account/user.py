from django.conf import settings
from django.contrib.auth.models import User

from account.kobra import name_from_liu_id, is_student
from account.models import Section
from account.section_membership import check_membership


def apply_admin_permissions(user):
    if user.username in settings.SYSTEM_ADMINS:
        user.is_staff = True
        user.is_superuser = True
        user.save()

       
def add_to_section_groups(user):
    sections = Section.objects.all()
    for section in sections:
        is_member = check_membership(user.username, section)
        if is_member:
            group = section.user_group
            user.groups.add(group)


def get_or_create_user_if_student(username):
    user = _get_existing_user(username)
    if user is None:
        print('Creating non-existing user')
        user = User.objects.create(username=username)

    apply_admin_permissions(user)
    add_to_section_groups(user)
    return user


def _get_existing_user(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None
