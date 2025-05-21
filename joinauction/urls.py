from django.urls import path
from . import views

urlpatterns = [
    
    path('check_auction_status/<int:auction_id>', views.check_auction_status, name='check_auction_status'),
    path('',views.join_meeting),
    path('player_data_send/<int:auction_id>', views.player_data_send, name='player_data_send'),
    path('get_budget/<int:auction_id>', views.get_budget, name='get_budget'),
    path('datapage/<int:auction_id>/<str:team_name>/', views.datapage_view, name='datapage'),
    path('hostdatapage/<int:auction_id>/', views.hostdatapage_view, name='hostdatapage'),
]
