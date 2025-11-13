# bots/balanced_bot.py
class BalancedBot:
    def __init__(self):
        self.name = "BalancedBot"
        
    def bet(self, state, memory=None):
        # Balanced ranges
        # Mixed strategies
        # Game theory optimal concepts
        hand_strength = self.get_hand_strength(state)
        
        # Use mixed strategy for certain decisions
        if hand_strength > 0.7:
            if random.random() < 0.8:  # 80% bet, 20% check-raise
                return self.value_bet(state), memory
            else:
                return 0, memory  # Check with intention to raise
        # ... more balanced logic

BOT_CLASS = BalancedBot