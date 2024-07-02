from django.contrib import admin, messages

from .models import Member, ProgramRegistration, Request
from .utils import check_membership


class ProgramRegistrationAdminInline(admin.TabularInline):
    # readonly_fields = ('registration', )
    model = ProgramRegistration


class MemberAdmin(admin.ModelAdmin):
    list_display = ("liu_id", "membership_type", "first_name", "last_name")
    list_filter = ("membership_type",)
    search_fields = ("first_name", "last_name", "liu_id")
    inlines = (ProgramRegistrationAdminInline,)


admin.site.register(Member, MemberAdmin)


program_codes = {
    "D": "6cddd",
    "U": "6cmju",
    "IT": "6cite",
    "IP": "6kipr",
    "CS": "6mics",
}


def accept_request(modeladmin, request, queryset):
    for member_request in queryset:
        member, created = Member.objects.get_or_create(
            liu_id=member_request.username,
            defaults={
                "first_name": member_request.first_name,
                "last_name": member_request.last_name,
            },
        )
        if created:
            registration = (
                program_codes[member_request.program]
                + "-1-ht"
                + str(member_request.starting_year)
            )

            ProgramRegistration.objects.create(member=member, registration=registration)
            member_request.delete()
        else:
            modeladmin.message_user(
                request,
                "Something went wrong, the issue is likely that "
                + member_request.username
                + " is already a member.",
                level=messages.ERROR,
            )
            return
    modeladmin.message_user(request, "Requests were successfully accepted.")


accept_request.short_description = "Accept selected member requests"


class RequestAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    list_display = (
        "username",
        "first_name",
        "last_name",
        "program",
        "starting_year",
        "message",
        "timestamp",
        "get_is_member",
    )

    def get_is_member(self, obj):
        return check_membership(obj.username)

    get_is_member.short_description = "Already member"
    get_is_member.boolean = True

    search_fields = ("username", "first_name", "last_name", "message")
    list_filter = ("program", "starting_year", "timestamp")
    actions = [accept_request]


admin.site.register(Request, RequestAdmin)
