# bots/calling_station_bot.py
class CallingStationBot:
    def __init__(self):
        self.name = "CallingStationBot"
    
    def bet(self, state, memory=None):
        my_index = state.index_to_action
        my_stack = state.held_money[my_index]
        my_current_bet = state.bet_money[my_index]
        max_bet = max(state.bet_money)
        call_amount = max_bet - my_current_bet
        can_check = (call_amount == 0)
        
        if can_check:
            return 0, memory
        else:
            if call_amount <= my_stack * 0.4:
                return min(call_amount, my_stack), memory
            else:
                return -1, memory

BOT_CLASS = CallingStationBot