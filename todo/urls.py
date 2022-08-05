from django.urls import path
from .views import (
    home,
    ListCreateTodoAPI,
    UpdateDeleteTodoAPI,
    ListCreateTaskAPI,
    UpdateDeleteTaskAPI
)

urlpatterns = [
    path('', home, name='home'),
    path('todo/', ListCreateTodoAPI.as_view(), name='todo-list-create-api'),
    path('todo/<id>/', UpdateDeleteTodoAPI.as_view(), name='todo-update-delete-api'),

    path('task/', ListCreateTaskAPI.as_view(), name='task-list-create-api'),
    path('task/<id>/', UpdateDeleteTaskAPI.as_view(), name='task-update-delete-api'),
]
