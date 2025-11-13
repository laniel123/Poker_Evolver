# bots/loose_aggressive_bot.py
import random

class LooseAggressiveBot:
    def __init__(self):
        self.name = "LooseAggressiveBot"
    
    def bet(self, state, memory=None):
        my_index = state.index_to_action
        my_stack = state.held_money[my_index]
        my_current_bet = state.bet_money[my_index]
        max_bet = max(state.bet_money)
        call_amount = max_bet - my_current_bet
        can_check = (call_amount == 0)
        pot_size = sum(max(0, bet) for bet in state.bet_money)
        
        my_cards = getattr(state, 'player_cards', [])
        if len(my_cards) < 2:
            if can_check:
                return 0, memory
            elif call_amount <= state.big_blind:
                return min(call_amount, my_stack), memory
            else:
                return -1, memory
        
        card1, card2 = my_cards
        v1, s1 = self.parse_card(card1)
        v2, s2 = self.parse_card(card2)
        v_high, v_low = max(v1, v2), min(v1, v2)
        
        playable = (v_high >= 8 or v_low >= 6 or (v_high - v_low <= 3))
        
        if can_check:
            if playable and random.random() < 0.7:
                bet_size = min(int(pot_size * 0.5), my_stack)
                return max(bet_size, state.big_blind), memory
            else:
                return 0, memory
        else:
            if playable:
                if random.random() < 0.3 and call_amount <= my_stack * 0.3:
                    return min(call_amount * 2, my_stack), memory
                else:
                    return min(call_amount, my_stack), memory
            else:
                if call_amount <= state.big_blind:
                    return min(call_amount, my_stack), memory
                else:
                    return -1, memory
    
    def parse_card(self, cs):
        if isinstance(cs, str) and len(cs) == 2:
            v, s = cs[0].lower(), cs[1].lower()
            val_to_int = {"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"t":10,"j":11,"q":12,"k":13,"a":14}
            return val_to_int.get(v, 2), s
        return 2, "s"

BOT_CLASS = LooseAggressiveBot