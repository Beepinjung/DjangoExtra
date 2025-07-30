from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Task, Profile

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_secret', 'created_at')
    list_filter = ('is_secret', 'created_at')
    search_fields = ('title', 'description')

admin.site.register(Task, TaskAdmin)
admin.site.register(Profile)
