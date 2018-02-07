from django.contrib import admin

from voting.models import Section, Meeting, Scanner, Attendant, Vote, Alternative, MadeVote


class SectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    readonly_fields = ('user_group', 'admin_group')


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'archived')


class ScannerAdmin(admin.ModelAdmin):
    list_display = ('user', 'meeting')


class AttendantAdmin(admin.ModelAdmin):
    list_display = ('user', 'meeting')


class VoteAdmin(admin.ModelAdmin):
    list_display = ('question', 'meeting', 'open')


class AlternativeAdmin(admin.ModelAdmin):
    list_display = ('vote', 'text', 'num_votes')
    list_display_links = ('vote', 'text')


class MadeVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'vote')


admin.site.register(Section, SectionAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Scanner, ScannerAdmin)
admin.site.register(Attendant, AttendantAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Alternative, AlternativeAdmin)
admin.site.register(MadeVote, MadeVoteAdmin)
