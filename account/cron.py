# """
# Maintains a mirror of the excel sheet used to keep track of the user
# memberships in the various section committees.
# """

# import kronos
# from django.contrib.auth.models import User, Group

# from account.sheet import Sheet, LIU_ID, UTSKOTT, NAME


# @kronos.register('* * * * * *')
# def update_mirror():
#     """
#     Synchronizes the list of "sektionsaktiva" with the Django user/group database.

#     This method is configured to execute every hour. This periodic task must be
#     setup by running:
#       $ python manage.py installtasks

#     The command can be executed manually by executing:
#       $ python manage.py runtask update_mirror
#     """

#     sheet = Sheet()
#     data = sheet.read_data()

#     groups = {}

#     # Create all users and groups. Store the new group members in a list.
#     for row in data:
#         user = _store_user(row)
#         group = _store_group(row)

#         if group not in groups:
#             groups[group] = []

#         new_users_in_group = groups[group]
#         new_users_in_group.append(user)

#     # Update group membership
#     for group, new_users_in_group in groups.items():
#         previous_users_in_group = User.objects.filter(groups__name=group.name)

#         # Remove old members
#         for current_member in previous_users_in_group:
#             if current_member not in new_users_in_group:
#                 current_member.groups.remove(group)

#         # Add new members
#         for new_member in new_users_in_group:
#             new_member.groups.add(group)


# def _store_user(row):
#     """
#     Stores the user in the row as a Django user.
#     """

#     username = row[LIU_ID].lower()
#     user, created = User.objects.get_or_create(username=username)

#     first_name, last_name = _names(row)

#     user.first_name = first_name
#     user.last_name = last_name
#     user.save()

#     return user


# def _store_group(row):
#     """
#     Stores the utskott in the row as a Django group.
#     """

#     utskott = row[UTSKOTT]
#     group, created = Group.objects.get_or_create(name=utskott)

#     return group


# def _names(row):
#     """
#     Splits the full name into first and last name. This is generally a bad thing
#     to do but this is purely for presentational purposes.

#     For details, see https://stackoverflow.com/a/259694.
#     """

#     split = row[NAME].split()
#     first = split[0]
#     last = ' '.join(split[1:])

#     return first, last
