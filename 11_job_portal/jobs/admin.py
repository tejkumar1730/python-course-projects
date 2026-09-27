from django.contrib import admin
from .models import Application, Company, Job, Profile

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "location", "employment_type", "is_active"]
    list_filter = ["is_active", "employment_type"]
    search_fields = ["title", "company__name", "location"]

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["candidate", "job", "status", "applied_at"]
    list_filter = ["status"]

admin.site.register(Company)
admin.site.register(Profile)
