from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    # path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('',  include('todo.urls')),
    path('admin/', admin.site.urls),
]
