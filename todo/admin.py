from django.contrib import admin

from .models import Task, Todo, SubTask

admin.site.register(Task)
admin.site.register(Todo)
admin.site.register(SubTask)
