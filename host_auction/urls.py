from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.tournament_view,name='tournament_view'),   
]
