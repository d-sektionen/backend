from django.contrib import admin

from voting.models import Section, Meeting, Scanner, Attendant, Vote, Alternative, MadeVote

admin.site.register(Section)
admin.site.register(Meeting)
admin.site.register(Scanner)
admin.site.register(Attendant)
admin.site.register(Vote)
admin.site.register(Alternative)
admin.site.register(MadeVote)
