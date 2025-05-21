from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/',include('register.urls')),
    path('login/',include('login.urls')),
    path('home/',include('home.urls')),
    path('',include('home.urls')),
    path('host_auction/',include('host_auction.urls')),
    path('logout/',include('logout.urls')),
    path('status/',include('status.urls')),
    path('joinauction/',include('joinauction.urls')),
]

