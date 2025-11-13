# enhanced_evolver.py
import json
import random
from typing import Dict, List

class EnhancedEvolver:
    def __init__(self):
        self.advanced_param_ranges = {
            # Core parameters
            "PREM_OPEN_MULT_MEAN": (2.0, 6.0),
            "STRONG_OPEN_MULT_MEAN": (1.5, 4.0),
            "MEDIUM_OPEN_FREQ": (0.1, 0.8),
            
            # Advanced postflop parameters
            "POSTFLOP_BET_THRESHOLD": (0.3, 0.7),
            "POSTFLOP_BET_FREQ": (0.4, 0.9),
            "POSTFLOP_RAISE_FREQ": (0.2, 0.6),
            
            # Bluffing parameters
            "BLUFF_FREQUENCY": (0.05, 0.3),
            "SEMI_BLUFF_FREQUENCY": (0.1, 0.4),
            
            # Adaptation parameters
            "ADAPT_AGGRESSION_RATE": (0.1, 0.5),
            "OPPONENT_MODELING": (0.0, 1.0),
            
            # Position awareness
            "BTN_OPEN_RANGE": (0.1, 0.8),
            "SB_OPEN_RANGE": (0.05, 0.4),
            
            # Pot control
            "POT_CONTROL_FREQUENCY": (0.1, 0.6),
            "CHECK_RAISE_FREQUENCY": (0.05, 0.4)
        }
    
    def evolve_bot_v3_strategies(self):
        """Evolve multiple strategic dimensions"""
        
        # 1. Preflop Strategy Evolution
        print("Evolving preflop strategies...")
        preflop_params = self.evolve_dimension(["tight_bot", "loose_aggressive_bot"], 
                                            ["PREM_OPEN_MULT_MEAN", "STRONG_OPEN_MULT_MEAN", "MEDIUM_OPEN_FREQ"])
        
        # 2. Postflop Strategy Evolution  
        print("Evolving postflop strategies...")
        postflop_params = self.evolve_dimension(["smart_bot", "balanced_bot"],
                                              ["POSTFLOP_BET_THRESHOLD", "POSTFLOP_BET_FREQ", "POSTFLOP_RAISE_FREQ"])
        
        # 3. Bluffing Strategy Evolution
        print("Evolving bluffing strategies...")
        bluff_params = self.evolve_dimension(["calling_station_bot", "bluffing_bot"],
                                           ["BLUFF_FREQUENCY", "SEMI_BLUFF_FREQUENCY"])
        
        # Combine all evolved strategies
        bot_v3_strategy = {**preflop_params, **postflop_params, **bluff_params}
        
        return bot_v3_strategy
    
    def evolve_dimension(self, opponents: List[str], params: List[str], generations: int = 20):
        """Evolve specific strategic dimension"""
        param_ranges = {p: self.advanced_param_ranges[p] for p in params}
        
        # Run focused evolution
        best_strategy = run_focused_evolution(
            evolving_bot="bot_v2_test",
            opponents=opponents,
            param_ranges=param_ranges,
            generations=generations
        )
        
        return best_strategy