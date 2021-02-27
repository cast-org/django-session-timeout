from django.urls import path
from . import views

urlpatterns = [
    path('status', views.status, name='status'),
    path('keepalive', views.keepalive, name='keepalive'),
    path('expire', views.expire, name='expire'),
]
