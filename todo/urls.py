from django.urls import path
from .views import (
    home,
    CreateTodoAPI,
    UpdateDeleteTodoAPI,
    CreateTaskAPI,
    UpdateDeleteTaskAPI,
    CreateSubClassUsingIdsAPI,
    CreateSubClassUsingDataAPI,
)

urlpatterns = [
    path('', home, name='home'),
    path('todo/', CreateTodoAPI.as_view(), name='todo-create-api'),
    path('todo/<id>/', UpdateDeleteTodoAPI.as_view(), name='todo-update-delete-api'),

    path('task/', CreateTaskAPI.as_view(), name='task-create-api'),
    path('task/<id>/', UpdateDeleteTaskAPI.as_view(), name='task-update-delete-api'),

    path('sub-task-ids/', CreateSubClassUsingIdsAPI.as_view(), name='sub-task-create-ids-api'),
    path('sub-task-data/', CreateSubClassUsingDataAPI.as_view(), name='sub-task-create-data-api'),
]
