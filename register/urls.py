
from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.register_view, name='register'),
    path('verify-email/',views.verify_email, name='verify_view'),
]
