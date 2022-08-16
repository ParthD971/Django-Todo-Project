from django.urls import path
from .views import (
    home,
    CreateTodoAPI,
    UpdateDeleteTodoAPI,
    CreateTaskAPI,
    UpdateDeleteTaskAPI,
    CreateSubTaskUsingIdsAPI,
    CreateSubTaskUsingDataAPI,
)

urlpatterns = [
    path('', home, name='home'),
    path('todo/', CreateTodoAPI.as_view(), name='todo-create-api'),
    path('todo/<id>/', UpdateDeleteTodoAPI.as_view(), name='todo-update-delete-api'),

    path('task/', CreateTaskAPI.as_view(), name='task-create-api'),
    path('task/<id>/', UpdateDeleteTaskAPI.as_view(), name='task-update-delete-api'),

    path('sub-task-ids/', CreateSubTaskUsingIdsAPI.as_view(), name='sub-task-create-ids-api'),
    path('sub-task-data/', CreateSubTaskUsingDataAPI.as_view(), name='sub-task-create-data-api'),
]
