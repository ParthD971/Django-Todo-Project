from django.urls import path
from .views import (
    CreateTodoAPI,
    UpdateDeleteTodoAPI,
    CreateTaskAPI,
    UpdateDeleteTaskAPI,
    CreateSubTaskUsingIdsAPI,
    CreateSubTaskUsingDataAPI,
)

urlpatterns = [
    path('todo/', CreateTodoAPI.as_view(), name='todo-create-drf-api'),
    path('todo/<id>/', UpdateDeleteTodoAPI.as_view(), name='todo-update-delete-drf-api'),

    path('task/', CreateTaskAPI.as_view(), name='task-create-drf-api'),
    path('task/<id>/', UpdateDeleteTaskAPI.as_view(), name='task-update-delete-drf-api'),

    path('sub-task-ids/', CreateSubTaskUsingIdsAPI.as_view(), name='sub-task-create-ids-drf-api'),
    path('sub-task-data/', CreateSubTaskUsingDataAPI.as_view(), name='sub-task-create-data-drf-api'),
]
