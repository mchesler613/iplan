from django.contrib import admin
from planner.models import *

class PersonAdmin(admin.ModelAdmin):
    # list_display provides headers for the fields
    list_display =('pk', 'name', 'status', 'age')

class BioAdmin(admin.ModelAdmin):
    list_display = ('pk', 'bio', 'person')
    search_fields = ('bio', 'person__name')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description', 'person')
    search_fields = ('title', 'description', 'person__name')

class MeetingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'purpose', 'date', 'time', 'list_participants')
    search_fields = ['title', 'purpose', 'participants__name']

    def list_participants(self, obj):
        return obj.participants.values_list('name', flat=True)

class EmailAdmin(admin.ModelAdmin):
    list_display = ('pk', 'address', 'person')
    search_fields = ['address', 'person__name']

# Register your models here.
admin.site.register(Person, PersonAdmin)
admin.site.register(Bio, BioAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Email, EmailAdmin)
