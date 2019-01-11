from django.contrib import admin

from .models import Member, ProgramRegistration

class ProgramRegistrationAdminInline(admin.TabularInline):
    # readonly_fields = ('registration', )
    model = ProgramRegistration

class MemberAdmin(admin.ModelAdmin):
    list_display = ('liu_id', 'membership_type', 'first_name', 'last_name',)
    inlines = (ProgramRegistrationAdminInline, )

admin.site.register(Member, MemberAdmin)

# class ProgramRegistrationAdmin(admin.ModelAdmin):
#     readonly_fields = ('member', 'registration')

# admin.site.register(ProgramRegistration, ProgramRegistrationAdmin)
