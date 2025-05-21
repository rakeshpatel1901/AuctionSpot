from django.urls import path,re_path
from .consumer import *

ws_patterns = [
      path('ws/auction/', PlayerDataConsumer.as_asgi()),
      re_path(r'ws/data/(?P<auction_id>\d+)/$', DataConsumer.as_asgi()),
      re_path(r'ws/individualdata/(?P<auction_id>\d+)/$', IndividualDataConsumer.as_asgi()),
     
]