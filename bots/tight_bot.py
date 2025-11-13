# bots/tight_bot.py
import random

class TightBot:
    def __init__(self):
        self.name = "TightBot"
    
    def bet(self, state, memory=None):
        my_index = state.index_to_action
        my_stack = state.held_money[my_index]
        my_current_bet = state.bet_money[my_index]
        max_bet = max(state.bet_money)
        call_amount = max_bet - my_current_bet
        can_check = (call_amount == 0)
        
        my_cards = getattr(state, 'player_cards', [])
        if len(my_cards) < 2:
            return 0, memory
        
        card1, card2 = my_cards
        v1, s1 = self.parse_card(card1)
        v2, s2 = self.parse_card(card2)
        v_high, v_low = max(v1, v2), min(v1, v2)
        suited = (s1 == s2)
        paired = (v1 == v2)
        
        premium = (paired and v_high >= 10) or (v_high == 14 and v_low >= 12)
        strong = (paired and v_high >= 8) or (v_high == 14 and v_low >= 10)
        
        if can_check:
            if premium:
                return min(int(state.big_blind * 3), my_stack), memory
            elif strong and random.random() < 0.3:
                return min(int(state.big_blind * 2), my_stack), memory
            else:
                return 0, memory
        else:
            if premium:
                return min(call_amount, my_stack), memory
            elif strong and call_amount <= state.big_blind * 2:
                return min(call_amount, my_stack), memory
            else:
                return -1, memory
    
    def parse_card(self, cs):
        if isinstance(cs, str) and len(cs) == 2:
            v, s = cs[0].lower(), cs[1].lower()
            val_to_int = {"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"t":10,"j":11,"q":12,"k":13,"a":14}
            return val_to_int.get(v, 2), s
        return 2, "s"

# Required export
BOT_CLASS = TightBot