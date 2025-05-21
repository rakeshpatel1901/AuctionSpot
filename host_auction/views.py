from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from . import models
from django.http import HttpResponse
import csv
from datetime import datetime
import random
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.

def generate_id():
    return str(random.randint(100000,999999));
def generate_password():
    return str(random.randint(1000,9999));
def send_meeting_detail(user_email, meeting_id, meeting_password,tournament_name,auctiondate):
    subject = "AUCTION DETAILS : "+str(tournament_name)
    message = f"The {tournament_name} auction is held on {auctiondate} :\n Meeting Id :  {meeting_id} \n Password : {meeting_password}"
    from_email = settings.EMAIL_HOST_USER  
    send_mail(subject, message, from_email, [user_email])
def tournament_view(request):
    if request.method == 'POST': 
        tournament_name = request.POST.get('tournament_name')
        tournament_category = request.POST.get('tournament_category')
        budget = request.POST.get('budget')
        min_player = request.POST.get('min_player')
        max_player = request.POST.get('max_player')
        tournament_description = request.POST.get('tournament_description')
        auctiondate = request.POST.get('auctiondate')
        total_teams = request.POST.get('total_teams')
        csv_file = request.FILES.get('csv_file')
        print("FILES content:", request.FILES)
        if csv_file:
            # Check if the uploaded file has a .csv extension
            if not csv_file.name.endswith('.csv'):
                return HttpResponse("Please upload a valid CSV file.")
            try:
                # Decode and process the CSV file
                auction_datetime = datetime.strptime(auctiondate, '%Y-%m-%dT%H:%M')
                csv_data = csv.reader(csv_file.read().decode('utf-8').splitlines())
                
                # Save tournament and auction details
                user_email = request.session.get('user_email')
                user = User.objects.get(email=user_email)
                tournament = models.tournament.objects.create(
                    tournament_name=tournament_name,
                    tournament_category=tournament_category,
                    budget=budget,
                    min_player=min_player,
                    max_player=max_player,
                    tournament_description=tournament_description,
                )
                auction = models.Auction_db.objects.create(
                    auction_datetime=auction_datetime,
                    tournament=tournament,
                    user=user,
                )
                meeting_id = generate_id()
                meeting_password = generate_password()  
                meeting = models.Auction_meeting.objects.create(
                    meeting_id=meeting_id,
                    meeting_password=meeting_password,
                    total_team=total_teams, 
                    auction=auction,
                )
                if(tournament_category == 'Cricket'):
                    for row in csv_data:
                        playername = row[0]
                        matchesplayed = row[1]
                        playerrole = row[2]
                        playerage = row[3]
                        runs = row[4]
                        ball_played = row[5]
                        ball_bowled = row[6]
                        wicket = row[7]
                        player = models.player_db.objects.create(
                            player_name=playername,
                            matches_played=matchesplayed,
                            player_role=playerrole,
                            player_age=playerage,
                            sport =  tournament_category,
                            auction = auction,
                        )
                        playerstats = models.player_cricket.objects.create(
                            runs = runs,
                            balls_played = ball_played,
                            balls_bowled = ball_bowled,
                            wickets = wicket,
                            player=player,
                        )
                        player.save()
                        playerstats.save()
                elif(tournament_category == 'Football'):
                    pass;
                tournament.save()
                auction.save()
                user_email = request.session.get('user_email')
                send_meeting_detail(user_email, meeting_id, meeting_password,tournament_name,auction_datetime)
                meeting.save()
                return redirect('../home')
            except Exception as e:
                print("Error creating:", e)
                return HttpResponse("An error occurred while creating the tournament and auction.")
        else:
            return HttpResponse("Please upload a file.")
    if(request.session.get('user_email')):
        return render(request, 'tournament.html')
    else:
        return redirect('../home')