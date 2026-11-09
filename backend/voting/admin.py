from django.contrib import admin
from django.db.models import Count

from ..voting.models import (
    Meeting,
    Attendant,
    Vote,
    Alternative,
    Ballot,
    MadeVote,
    SpeakerRequest,
)


class MeetingAdmin(admin.ModelAdmin):
    list_display = ("name", "archived")


class AttendantAdmin(admin.ModelAdmin):
    list_display = ("user", "meeting")


class VoteAdmin(admin.ModelAdmin):
    list_display = ("question", "meeting", "open")


class SpeakerRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "meeting")


class AlternativeAdmin(admin.ModelAdmin):
    list_display = ("vote", "text", "num_votes")
    list_display_links = ("vote", "text")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(num_votes=Count("ballot"))

    @admin.display(description="num votes", ordering="num_votes")
    def num_votes(self, obj):
        return obj.num_votes


class BallotAdmin(admin.ModelAdmin):
    list_display = ("alternative",)


class MadeVoteAdmin(admin.ModelAdmin):
    list_display = ("user", "vote")


admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Attendant, AttendantAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Alternative, AlternativeAdmin)
admin.site.register(Ballot, BallotAdmin)
admin.site.register(MadeVote, MadeVoteAdmin)
admin.site.register(SpeakerRequest, SpeakerRequestAdmin)
