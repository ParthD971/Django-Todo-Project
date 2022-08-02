from django.contrib import admin
from django.urls import path, include
import social_django.urls
urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('',  include('todo.urls')),
    path('admin/', admin.site.urls),
]
