from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from host_auction import models
from django.http import HttpResponse



def status_view(request):
    if request.method == 'POST':
        try:
            auctionid = request.POST.get('auction_id')
            action = request.POST.get('action')
            auction = models.Auction_db.objects.get(auction_id=auctionid)
            if not auctionid:
                return HttpResponse("Auction ID is required.")
            
            if action == 'cancel':
                playerid = models.player_db.objects.filter(auction__auction_id=auctionid)
                for player in playerid:
                    models.player_cricket.objects.filter(player=player).delete()
                    models.player_football.objects.filter(player=player).delete()
                playerid.delete() 
                auction = models.Auction_db.objects.filter(auction_id=auctionid).first()
                tournament = auction.tournament
                auction.delete()  
                if not models.Auction_db.objects.filter(tournament=tournament).exists():
                    tournament.delete()  # Delete the tournament if no auctions are left
                    '''
                    models.tournament.objects.filter(auction_id=auctionid).delete()  # Delete tournament
                    '''
                    
                return redirect('status')
            elif action == 'join':
                return render(request, 'host_auction_page.html', {'data': auction, 'val': 'join','auctionid':auctionid})
            elif action == 'start':
                auction.auction_status = 'started'
                auction.save()
                return render(request, 'host_auction_page.html', {'data': auction, 'val':'start'})
            
        except Exception as e:
            return HttpResponse(e)
    
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login') 
    
    try:
        user = User.objects.get(email=user_email)
        auction = models.Auction_db.objects.filter(user=user)
        return render(request, 'status.html', {'auction': auction})
    except User.DoesNotExist:
        return render(request, 'status.html', {'error': 'User not found.'}) 
    except models.Auction_db.DoesNotExist:
        return render(request, 'status.html', {'error': 'No auction found for the user.'})


