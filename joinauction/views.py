from django.shortcuts import render, redirect
from django.http import JsonResponse

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def join_meeting(request):
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        meeting_id = request.POST.get('meeting_id')
        meeting_password = request.POST.get('meeting_password')
        print(meeting_id)
        print(meeting_password)
        from host_auction.models import Auction_meeting
        # Check if meeting_id is provided
        if not meeting_id:
            return JsonResponse({'success': False, 'message': 'Meeting ID is required.'})

        # Fetch the meeting object or return an error
        try:
            meeting = Auction_meeting.objects.get(meeting_id=meeting_id)
        except Auction_meeting.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Meeting not found.'})

        # Validate the meeting password
        if meeting.meeting_password != meeting_password:
            return JsonResponse({'success': False, 'message': 'Incorrect meeting password.'})

        # Check if the team can join
        if int(meeting.joined_team) >= int(meeting.total_team):
            return JsonResponse({'success': False, 'message': 'Meeting is full.'})

        # Increment joined_team
        meeting.joined_team = str(int(meeting.joined_team) + 1)
        meeting.save()

        # Store team_name in session and redirect to auction page
        request.session['team_name'] = team_name
        auction_status = meeting.auction.auction_status  # Assuming this field exists
        waiting = auction_status != 'started'
        return render(request,'team_auction_page.html',{'auction_id':meeting.auction.auction_id,'waiting':waiting,'team_name':team_name})

    if(request.session.get('user_email')):
        return render(request, 'join_meeting.html')
        
    else:
        return redirect('../home')



def check_auction_status(request,auction_id):
    from host_auction.models import Auction_db
    try:

        auction = Auction_db.objects.get(auction_id=auction_id)
        if auction.auction_status == 'started':
            if request.session.get('status'):
                del request.session['status'];
                return JsonResponse({'status': 'Auction already started in session'})
            request.session['status']='started'
            return JsonResponse({'status': 'started'})
        else:
            return JsonResponse({'status': auction.auction_status})
    except Auction_db.DoesNotExist:
        return JsonResponse({'error': 'Auction not found'}, status=404)
    

#########################################
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render
from channels.layers import get_channel_layer
import time
import json

from django.http import JsonResponse

def player_data_send(request,auction_id):
    from host_auction.models import Auction_db,player_db,player_cricket,player_football
    print("INSIDE PLAYER DATA VIEWS")
    try:
        
        # Fetch the auction object
        auction = Auction_db.objects.get(auction_id=auction_id)
        print("Fetching auction status : ",auction.auction_status)

        # Fetch players associated with the auction
        players = player_db.objects.filter(auction=auction)

        if not players.exists():
            return JsonResponse({'error': 'No players found for this auction.'}, status=404)
        # Prepare player details
        player_details = []
        for player in players:
            print(player.player_name)
            player_detail = {}
            if player.sport == 'Cricket':
                play = player_cricket.objects.filter(player=player).first()
                if play:
                    player_detail.update({
                        'runs': play.runs,
                        'balls_played': play.balls_played,
                        'balls_bowled': play.balls_bowled,
                        'wicket': play.wickets,
                    })
            elif player.sport == 'Football':
                play = player_football.objects.filter(player=player).first()
                if play:
                    player_detail.update({
                        'goals': play.goals,
                        'assists': play.assists,
                        'tackles': play.tackles,
                        'goals_saved': play.goals_saved,
                    })

            # Common player details
            player_detail.update({
                'player_name': player.player_name,
                'matches_played': player.matches_played,
                'player_role': player.player_role,
                'sport': player.sport,
            })

            player_details.append(player_detail)

        # Broadcast player details via WebSocket
        # channel_layer = get_channel_layer()
        # await channel_layer.group_send(
        # "player_group",
        # {
        #     'type': 'player_data',  # Matches the method name in the consumer
        #     'value': player_details,  # Send as a dictionary
        # }
        # )

        # Return a success response
        return JsonResponse({'success': True, 'player_details': player_details})

    except Exception as e:
        # Log the error and return a 500 response
        print(f"Error in player_data_send: {e}")
        return JsonResponse({'error': 'An error occurred while processing player data.'}, status=500)

def get_budget(request, auction_id):
    from host_auction.models import Auction_db
    try:
        auction = Auction_db.objects.get(auction_id=auction_id)
        budget = auction.tournament.budget  # Assuming Auction_db has a ForeignKey to Tournament
        return JsonResponse({'budget':budget})
    except Auction_db.DoesNotExist:
        return JsonResponse({'error': 'Auction not found'}, status=404)
    


def datapage_view(request, auction_id, team_name):
    from host_auction.models import Auction_db, player_db, player_cricket, player_football, tournament
    from .models import Bid

    auction_data = Auction_db.objects.get(auction_id=auction_id)
    tournament_data = tournament.objects.get(tournament_id=auction_data.tournament.tournament_id)
    bid_data = Bid.objects.filter(tournament=tournament_data.tournament_id)
    player_ids = [bid.player.player_id for bid in bid_data]
    player_data = player_db.objects.filter(player_id__in=player_ids)

    # Prepare combined data (player name and bid amount)
    combined_data = [
        {
            "player_name": player.player_name,
            "bid_amount": bid.bid_amt,
        }
        for player, bid in zip(player_data, bid_data)
    ]

    context = {
        'auction_id': auction_id,
        'team_name': team_name,
        'tournament_name': auction_data.tournament,
        'combined_data': combined_data,
    }
    return render(request, 'datapage.html', context)


def hostdatapage_view(request, auction_id):
    from host_auction.models import Auction_db, player_db, player_cricket, player_football, tournament
    from joinauction.models import Bid

    auction_data = Auction_db.objects.get(auction_id=auction_id)
    auction_data.status = 1;
    auction_data.save();
    tournament_data = tournament.objects.get(tournament_id=auction_data.tournament.tournament_id)
    
    # Fetch bid data and order by team name
    bid_data = Bid.objects.filter(tournament=tournament_data.tournament_id).order_by('team_name')
    
 
 

    # Extract player IDs from bid data
    player_ids = [bid.player.player_id for bid in bid_data]
    player_data = player_db.objects.filter(player_id__in=player_ids)

    # Prepare combined data (player name, bid amount, team name)
    combined_data = [
        {
            "player_name": player.player_name,
            "bid_amount": bid.bid_amt,
            "team": bid.team_name,
        }
        for player, bid in zip(player_data, bid_data)
    ]

    context = {
        'auction_id': auction_id,
        'team_name': "All Teams",
        'tournament_name': auction_data.tournament,
        'combined_data': combined_data,
    }
    return render(request, 'hostdatapage.html', context)
