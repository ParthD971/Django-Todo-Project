from django.urls import path
from .views import (
    CreateTodoAPI,
    UpdateDeleteTodoAPI,
    CreateTaskAPI,
    UpdateDeleteTaskAPI,
    CreateSubTaskUsingIdsAPI,
    CreateSubTaskUsingDataAPI,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
    openapi.Info(
        title="Jaseci API",
        default_version='v1',
        description="Welcome to the world of Jaseci",
        terms_of_service="https://www.jaseci.org",
        contact=openapi.Contact(email="jason@jaseci.org"),
        license=openapi.License(name="Awesome IP"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('todo/', CreateTodoAPI.as_view(), name='todo-create-drf-api'),
    path('todo/<id>/', UpdateDeleteTodoAPI.as_view(), name='todo-update-delete-drf-api'),

    path('task/', CreateTaskAPI.as_view(), name='task-create-drf-api'),
    path('task/<id>/', UpdateDeleteTaskAPI.as_view(), name='task-update-delete-drf-api'),

    path('sub-task-ids/', CreateSubTaskUsingIdsAPI.as_view(), name='sub-task-create-ids-drf-api'),
    path('sub-task-data/', CreateSubTaskUsingDataAPI.as_view(), name='sub-task-create-data-drf-api'),
]
