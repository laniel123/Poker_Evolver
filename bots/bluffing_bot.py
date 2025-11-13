# bots/bluffing_bot.py
import random

class BluffingBot:
    def __init__(self):
        self.name = "BluffingBot"
        self.bluff_frequency = 0.3
        
    def bet(self, state, memory=None):
        # Strategic bluffing
        # Semi-bluffing with draws
        # Bluff detection
        if self.should_bluff(state):
            return self.execute_bluff(state), memory
        else:
            return self.normal_play(state), memory

BOT_CLASS = BluffingBot