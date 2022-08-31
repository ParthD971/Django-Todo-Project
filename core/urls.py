from django.conf import settings
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('debug/', include('debug.urls')),

    path('',  include('todo.urls')),
    path('api/',  include('todo_in_drf.urls')),
    path('admin/', admin.site.urls),


]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
