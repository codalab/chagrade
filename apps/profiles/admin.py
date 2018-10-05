from django.contrib import admin

from apps.profiles.models import Instructor, ChaUser, StudentMembership, AssistantMembership

# Register your models here.

admin.site.register(Instructor)
admin.site.register(ChaUser)
admin.site.register(StudentMembership)
admin.site.register(AssistantMembership)
