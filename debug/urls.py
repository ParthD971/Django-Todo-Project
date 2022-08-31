from django.urls import path
from debug.views import Debug

urlpatterns = [
    path('', Debug.as_view(), name='debug'),
]
