from django.contrib import admin
from .models import Student
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display=['roll_number','name','course','score','enrolled']
    search_fields=['roll_number','name','course']
    list_filter=['course']
