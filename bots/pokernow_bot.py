# pokernow_bot.py
import requests
import websocket
import json

class PokerNowBot:
    def __init__(self, club_id, player_name="EvolvedBot"):
        self.club_id = club_id
        self.player_name = player_name
        self.ws = None
        
    def connect(self):
        """Connect to PokerNow game"""
        # PokerNow uses WebSocket for real-time communication
        self.ws = websocket.WebSocketApp(
            f"wss://server.pokernow.club/game/{self.club_id}",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open
        self.ws.run_forever()
    
    def on_message(self, ws, message):
        """Handle incoming game messages"""
        data = json.loads(message)
        
        if data.get('type') == 'game_state_update':
            game_state = data['game_state']
            if game_state.get('action_on_me'):
                # It's our turn to act
                action = self.decide_action(game_state)
                self.send_action(action)
    
    def decide_action(self, game_state):
        """Use your evolved bot logic to decide action"""
        # Convert PokerNow format to your bot's expected format
        converted_state = self.convert_pokernow_state(game_state)
        
        # Use your existing bot logic
        action, memory = self.your_bot.bet(converted_state, self.memory)
        return action
    
    def send_action(self, action):
        """Send action back to PokerNow"""
        if action == -1:
            self.ws.send(json.dumps({"type": "fold"}))
        elif action == 0:
            self.ws.send(json.dumps({"type": "check"}))
        else:
            self.ws.send(json.dumps({"type": "bet", "amount": action}))