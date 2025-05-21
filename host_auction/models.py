from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class tournament(models.Model):
    tournament_id = models.AutoField(primary_key=True);
    tournament_name = models.CharField(max_length=100);
    tournament_description = models.TextField(max_length=500);
    tournament_category = models.CharField(max_length=40);
    budget = models.CharField(max_length=20,default=0);
    min_player = models.CharField(max_length=20,default=0);
    max_player = models.CharField(max_length=20,default=0);

    def __str__(self):
        return self.tournament_name;

class Auction_db(models.Model):
    auction_id = models.AutoField(primary_key=True);    
    auction_datetime = models.DateTimeField();
    auction_status = models.CharField(max_length=20, default='waiting')
    status = models.CharField(max_length=2,default=0);
    tournament = models.ForeignKey(tournament,on_delete=models.CASCADE, related_name='auctions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user');

class Auction_meeting(models.Model):
    mid = models.AutoField(primary_key=True)
    meeting_id = models.CharField(max_length=10,default=0);
    meeting_password = models.CharField(max_length=6,default=0);
    total_team = models.CharField(max_length=10);
    joined_team = models.CharField(max_length=10 , default=0);
    auction = models.ForeignKey(Auction_db, on_delete=models.CASCADE, related_name='meetings');
    

class player_db(models.Model):
    player_id = models.AutoField(primary_key=True);
    player_name = models.CharField(max_length=100);
    matches_played = models.CharField(max_length=10);
    player_role = models.CharField(max_length=50);
    player_age = models.CharField(max_length=5);
    sport= models.CharField(max_length=20, choices=[('Football', 'Football'), ('Cricket', 'Cricket')]);
    is_viewed = models.BooleanField(default=False)
    auction = models.ForeignKey(Auction_db, on_delete=models.CASCADE, related_name='players',default=0)

    def __str__(self):
        return self.player_name;

class player_cricket(models.Model):
    pcid = models.AutoField(primary_key=True);
    runs = models.CharField(max_length=50);
    balls_played = models.CharField(max_length=50);
    balls_bowled = models.CharField(max_length=50);
    wickets = models.CharField(max_length=50);
    player = models.ForeignKey(player_db, on_delete=models.CASCADE, related_name='cricket_player');

class player_football(models.Model):
    pfid = models.AutoField(primary_key=True);
    goals = models.CharField(max_length=50);
    assists = models.CharField(max_length=50);
    tackles = models.CharField(max_length=50);
    goals_saved = models.CharField(max_length=50);
    player = models.ForeignKey(player_db, on_delete=models.CASCADE, related_name='football_player');