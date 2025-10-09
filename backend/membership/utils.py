"""
File for communication with this model.
Avoid querying the Member model directly in other apps, make helper functions here instead.
"""

from .models import Member

"""
Checks if a liu_id is a member. Returns True if person is a student member (has voting rights), otherwise False
"""


def check_membership(liu_id):
    member = None
    try:
        member = Member.objects.get(liu_id=liu_id)  # type: ignore[attr-defined]
    except Member.DoesNotExist:  # type: ignore[attr-defined]
        return False

    return member.membership_type == "S"


"""
Gets the first_name and last_name of a liu_id.

If the member does not exist it returns (None, None)
Empty strings can also be returned if a member exists, but has an empty name.
"""


def get_name(liu_id):
    member = None
    try:
        member = Member.objects.get(liu_id=liu_id)  # type: ignore[attr-defined]
    except Member.DoesNotExist:  # type: ignore[attr-defined]
        return None, None

    return member.first_name, member.last_name
