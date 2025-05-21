
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync

import json


class PlayerDataConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Set up group and accept connection
        self.room_name="player_consumer"
        self.room_group_name = "player_group"
        await(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({'status': 'Connected'}))

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        print(f"Received message: {message}")

         # Optionally send a response back to the frontend
        await self.send(text_data=json.dumps({
            'response': f"Message '{message}' received by backend!"
        }))

    async def player_data(self, event):
        data = event.get('value', {})
        print("Received player data:", data)

        # Send the data to the WebSocket client
        await self.send(text_data=json.dumps({
            'message': data.get('message', 'No message received')
        }))

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
import json
import asyncio


class DataConsumer(AsyncJsonWebsocketConsumer):
    auction_started = {}

    async def connect(self):
        # Extract auction_id from the URL
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.room_group_name = f"data_channel_{self.auction_id}"  # Unique group for each auction

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        self.interval = 5  # Initial interval in seconds
        self.current_index = 0
        
        # Fetch auction-specific data using the auction_id
        auction_data = await self.get_auction_data(self.auction_id)
        self.data = auction_data  # Store fetched auction data
        self.is_running = False  # Flag to track if sending has started
        print(len(self.data))

    async def disconnect(self, close_code):
        # Leave room group
       
        print(f"WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data):
        
        data = json.loads(text_data)
        

        if data.get('start_sending'):
            # Ensure data broadcasting only starts once per auction
            if not DataConsumer.auction_started.get(self.auction_id):
                DataConsumer.auction_started[self.auction_id] = True
                await self.start_broadcasting()

        # If client requests to stop, stop sending data but don't close the connection
        if data.get('stop_sending'):
            print("Stop sending data request received.")
            # Optionally, you can add logic to halt further data broadcasting.

        # Increase interval if the 'increase_interval' flag is received
        if data.get('increase_interval'):
            self.interval += 5  # Increase interval by 5 seconds

        if data.get('place_bid'):
            print("Inside the Consumer")
            player_id = data.get('player_id')
            bid_amount = data.get('bid_amount')

            if player_id and bid_amount:
                success, message = await self.handle_place_bid(player_id, bid_amount)
            # Send response back to the WebSocket client
                await self.send(text_data=json.dumps({
                    'success': success,
                    'message': message,
                }))
            

    async def handle_place_bid(self, player_id, bid_amount):
        from .models import Bid
        from host_auction.models import Auction_db
        try:
            # Fetch the player bid from the database or create a new one
            team_name = self.scope['session'].get('team_name')
            auction = await sync_to_async(Auction_db.objects.get)(auction_id=self.auction_id)
            
            player_bid, created = await sync_to_async(Bid.objects.get_or_create)(
                team_name = team_name,
                tournament=auction.tournament,
                player=player_id,

            )
            player_bid.bid_amt = bid_amount
            await sync_to_async(player_bid.save)()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_bid_update',
                    'player_id': player_id,
                    'bid_amount': bid_amount,
                }
            )
            return True, f"Bid placed successfully for Player {player_id} with amount {bid_amount}"   
        except Exception as e:
            return False, f"An error occurred while placing the bid: {str(e)}"
        
    async def send_bid_update(self, event):
        await self.send(text_data=json.dumps({
            'player_id': event['player_id'],
            'bid_amount': event['bid_amount'],
            'success': True,
        }))
    async def start_broadcasting(self):
        batch_size = 20  # Send data in batches of 20
        total_data = len(self.data)
        current_index = 0

        while current_index < total_data:
            # Send a batch of data
            batch = self.data[current_index:current_index + batch_size]
            await asyncio.sleep(1)  # Wait for the specified interval between sending data
            for data_row in batch:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'send_data',
                        'row': data_row,
                        'success': True
                    }
                )
                

                # Yield to the event loop to prevent timeouts
                await asyncio.sleep(0)  # Yield control to prevent blocking

            # Update the index for the next batch
            current_index += batch_size

        # Do not close the connection; keep it open for further interaction
        # Optionally, you can keep waiting for client messages

    async def get_auction_data(self, auction_id):
        # Fetch data from database
        from host_auction.models import Auction_db, player_db, player_cricket, player_football

        auction_data = []
        auction = await sync_to_async(Auction_db.objects.get)(auction_id=auction_id)
        players = await sync_to_async(list)(player_db.objects.filter(auction=auction))

        for player in players:
            player_detail = {
                'player_id': player.player_id,
                'player_name': player.player_name,
                'matches_played': player.matches_played,
                'player_role': player.player_role,
                'sport': player.sport,
            }

            if player.sport == 'Cricket':
                # Fetch additional details from cricket model
                play = await sync_to_async(player_cricket.objects.filter(player=player).first)()
                if play:
                    player_detail.update({
                        'runs': play.runs,
                        'balls_played': play.balls_played,
                        'balls_bowled': play.balls_bowled,
                        'wickets': play.wickets,
                    })
            elif player.sport == 'Football':
                # Fetch additional details from football model
                play = await sync_to_async(player_football.objects.filter(player=player).first)()
                if play:
                    player_detail.update({
                        'goals': play.goals,
                        'assists': play.assists,
                        'tackles': play.tackles,
                        'goals_saved': play.goals_saved,
                    })
            auction_data.append(player_detail)  # Append player details to the auction data list

        return auction_data


    async def send_data(self, event):
        try:
        # Fetch auction details asynchronously
          

        # Send data to the WebSocket client
            await self.send(text_data=json.dumps({
                'row': event['row'],  # Player data
                'success': event.get('success', True),  # Success flag (defaults to True)
                
            }))
        except Exception as e:
        # Handle any other exceptions that may occur
            await self.send(text_data=json.dumps({
                'success': False,
                'message': str(e),
            }))


### Try New Way

class IndividualDataConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Extract auction_id from the URL
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.room_group_name = f"individualdata_channel_{self.auction_id}"  # Unique group for each auction
        self.interval = 5
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Set up initial state
        self.current_index = 0
        self.is_running = False
        self.auction_data = await self.get_auction_data(self.auction_id)  # Pre-fetch all data once

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected with code: {close_code}")
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('place_bid'):
            from .models import Bid
            from host_auction.models import Auction_db,player_db,tournament
            # Place bid
            try:
                print("Inside Place bid")
                team_name = data.get('team_name');
                print(team_name)
                player_id = data.get('player_id')
                bid_amount = data.get('bid_amount')
                auction = await sync_to_async(Auction_db.objects.get)(auction_id=self.auction_id)
                tournament_data = await sync_to_async(tournament.objects.get)(tournament_id=auction.tournament_id)
                player = await sync_to_async(player_db.objects.get)(player_id=player_id)
                bid, created = await sync_to_async(Bid.objects.get_or_create)(
                    player=player,
                    team_name=team_name,
                    tournament=tournament_data,
                )

            # Update or create the bid
                bid.bid_amt = bid_amount
                await sync_to_async(bid.save)()
                player_data = self.auction_data[self.current_index]
                if (player_data['player_id'] == player_id):
                    print("Got player_id")
                    player_data['bidAmount'] = bid_amount*2
                await self.send_player_data(player_data)
                await self.broadcast_player_data(player_data)
            except Exception as e:
                print(f"An error occurred while placing the bid: {str(e)}")
        
        if data.get('fetch_next_player'):
            # print(len(self.auction_data))
            # Fetch and send the next player's data
            await asyncio.sleep(15)
            if self.current_index < len(self.auction_data):
                print(self.auction_data[self.current_index])
                player_data = self.auction_data[self.current_index]
                self.current_index += 1
                await self.send_player_data(player_data)
                await self.broadcast_player_data(player_data)
            else:
                player_data = {'player_id':"No", 'player_name':"No"}
                await self.send_player_data(player_data)
                await self.broadcast_player_data(player_data)

    async def get_auction_data(self, auction_id):
        # Fetch all player data for the auction
        from host_auction.models import Auction_db, player_db, player_cricket, player_football

        auction = await sync_to_async(Auction_db.objects.get)(auction_id=auction_id)
        players = await sync_to_async(list)(player_db.objects.filter(auction=auction))

        auction_data = []
        for player in players:
            player_detail = {
                'player_id': player.player_id,
                'player_name': player.player_name,
                'player_age': player.player_age,
                'matches_played': player.matches_played,
                'player_role': player.player_role,
                'sport': player.sport,
                'bidAmount':200,
            }

            if player.sport == 'Cricket':
                play = await sync_to_async(player_cricket.objects.filter(player=player).first)()
                if play:
                    player_detail.update({
                        'runs': play.runs,
                        'balls_played': play.balls_played,
                        'balls_bowled': play.balls_bowled,
                        'wickets': play.wickets,
                    })
            elif player.sport == 'Football':
                play = await sync_to_async(player_football.objects.filter(player=player).first)()
                if play:
                    player_detail.update({
                        'goals': play.goals,
                        'assists': play.assists,
                        'tackles': play.tackles,
                        'goals_saved': play.goals_saved,
                    })

            auction_data.append(player_detail)
            player.is_viewed = True
            await sync_to_async(player.save)()

        return auction_data
    async def broadcast_player_data(self, player_data):
        # Send player data to all clients in the group (broadcasting)
        await self.channel_layer.group_send(
            self.room_group_name,  # Group name
            {
                'type': 'send_player_data',  # Handler for the message
                'player_data': player_data,
                'success': True,
            }
        )
    
    async def send_player_data(self, player_data):
        # Send a single player's data to the frontend
        try:
            await self.send(text_data=json.dumps({
                'player_data': player_data,
                'success': True,
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'success': False,
                'message': str(e),
            }))
