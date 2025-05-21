from django.db import models
from host_auction.models import player_db,tournament


class Bid(models.Model):
    bid_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    team_name = models.CharField(max_length=100,default='anonymous')  # Dynamic team name
    tournament = models.ForeignKey(tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(player_db, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)