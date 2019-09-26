from django.urls import path
from . import views

urlpatterns = [
    path('expire', views.expire, name='expire'),
]
