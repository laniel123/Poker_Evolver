# overnight_evolver.py
import json
import time
import os
import signal
import sys
from datetime import datetime, timedelta
from evolver import run_evolution, BotManager

class OvernightEvolver:
    def __init__(self, total_hours=8):
        self.total_hours = total_hours
        self.start_time = time.time()
        self.end_time = self.start_time + (total_hours * 3600)
        self.results_dir = "overnight_results"
        self.bot_manager = BotManager()
        self.setup_signal_handlers()
        
        os.makedirs(self.results_dir, exist_ok=True)
        
    def setup_signal_handlers(self):
        """Handle graceful shutdown"""
        def signal_handler(sig, frame):
            print(f"\n🛑 Received interrupt signal. Shutting down gracefully...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def cleanup(self):
        """Cleanup before exit"""
        print("🧹 Cleaning up...")
        self.save_final_checkpoint()
    
    def run_overnight_evolution(self):
        """Run continuous evolution for specified hours"""
        print("🌙 OVERNIGHT POKER BOT EVOLUTION")
        print("=" * 60)
        print(f"⏰ Running for {self.total_hours} hours")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🕐 Will end: {(datetime.now() + timedelta(hours=self.total_hours)).strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Get all available opponents
        all_opponents = [bot for bot in self.bot_manager.available_bots.keys() if bot != "bot_v2_test"]
        
        best_strategy = None
        best_fitness = 0
        total_generations = 0
        
        while time.time() < self.end_time:
            time_remaining = (self.end_time - time.time()) / 3600
            print(f"\n🕐 Time remaining: {time_remaining:.1f} hours")
            
            # Adjust strategy based on remaining time
            if time_remaining > 4:
                # Phase 1: Broad exploration
                opponents = all_opponents[:3]  # First 3 opponents
                generations = 5
                population_size = 20
                phase_name = "exploration"
            elif time_remaining > 2:
                # Phase 2: Focused refinement
                opponents = all_opponents[3:] if len(all_opponents) > 3 else all_opponents
                generations = 3
                population_size = 15
                phase_name = "refinement"
            else:
                # Phase 3: Final optimization
                opponents = all_opponents
                generations = 2
                population_size = 10
                phase_name = "final"
            
            print(f"🎯 {phase_name.upper()} PHASE: {generations} gens vs {opponents}")
            
            # Run evolution block
            initial_pop = [best_strategy] if best_strategy else None
            strategy, fitness = run_evolution(
                evolving_bot="bot_v2_test",
                opponents=opponents,
                generations=generations,
                population_size=population_size,
                initial_population=initial_pop
            )
            
            total_generations += generations
            
            # Update best strategy
            if fitness > best_fitness:
                best_strategy = strategy
                best_fitness = fitness
                print(f"🔥 NEW OVERALL BEST: {best_fitness:.3f}")
            
            # Save checkpoint
            self.save_checkpoint(total_generations, best_strategy, best_fitness, phase_name)
            
            # Safety sleep to prevent overheating
            time.sleep(2)
        
        # Final results
        self.save_final_results(best_strategy, best_fitness, total_generations)
        self.generate_bot_v3(best_strategy)
        
        print("\n" + "=" * 60)
        print("🌅 OVERNIGHT EVOLUTION COMPLETE!")
        print(f"🏆 Final Fitness: {best_fitness:.3f}")
        print(f"🧬 Total Generations: {total_generations}")
        print(f"⏰ Total time: {(time.time() - self.start_time) / 3600:.2f} hours")
        print("✅ bot_v3.py generated with evolved strategies!")
    
    def save_checkpoint(self, generation, strategy, fitness, phase):
        """Save progress checkpoint"""
        checkpoint = {
            'generation': generation,
            'best_strategy': strategy,
            'best_fitness': fitness,
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            'elapsed_hours': (time.time() - self.start_time) / 3600
        }
        
        filename = f"checkpoint_gen_{generation}.json"
        with open(os.path.join(self.results_dir, filename), 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        # Also save current best
        with open(os.path.join(self.results_dir, "current_best.json"), 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        print(f"💾 Checkpoint saved: {filename} (Fitness: {fitness:.3f})")
    
    def save_final_checkpoint(self):
        """Save final checkpoint on interruption"""
        try:
            # Try to load current best
            with open(os.path.join(self.results_dir, "current_best.json"), 'r') as f:
                current = json.load(f)
            
            current['interrupted'] = True
            current['final_timestamp'] = datetime.now().isoformat()
            
            with open(os.path.join(self.results_dir, "interrupted_final.json"), 'w') as f:
                json.dump(current, f, indent=2)
            
            print("💾 Final checkpoint saved (interrupted)")
        except:
            pass
    
    def save_final_results(self, strategy, fitness, total_generations):
        """Save final results"""
        final_results = {
            'final_strategy': strategy,
            'final_fitness': fitness,
            'total_generations': total_generations,
            'total_hours': (time.time() - self.start_time) / 3600,
            'completion_time': datetime.now().isoformat()
        }
        
        with open(os.path.join(self.results_dir, "final_results.json"), 'w') as f:
            json.dump(final_results, f, indent=2)
    
    def generate_bot_v3(self, strategy):
        """Generate bot_v3 with evolved strategies"""
        bot_v3_content = f'''# === BOT_V3 - OVERNIGHT EVOLVED BOT ===
# Generated from {self.total_hours} hours of evolution
# Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

from __future__ import annotations
from typing import List
import random

# EVOLVED PARAMETERS - Optimized overnight
PARAMS = {json.dumps(strategy, indent=2)}

class BotV3:
    """Overnight-evolved poker bot"""
    
    def __init__(self):
        self.name = "BotV3"
    
    def bet(self, state, memory=None):
        """Evolved decision making"""
        try:
            my_index = state.index_to_action
            my_stack = state.held_money[my_index]
            my_current_bet = state.bet_money[my_index]
            max_bet = max(state.bet_money)
            call_amount = max_bet - my_current_bet
            pot_size = sum(max(0, bet) for bet in state.bet_money)
            can_check = (call_amount == 0)
            is_preflop = (len(state.community_cards) == 0)
            
            my_cards = getattr(state, 'player_cards', [])
            if not my_cards or len(my_cards) < 2:
                if can_check:
                    return 0, memory
                else:
                    return min(call_amount, my_stack) if call_amount <= state.big_blind * 2 else -1, memory

            # Use evolved parameters for all decisions
            # Add your existing bot_v2_test logic here, using PARAMS
            # This is a simplified version - include your full logic
            
            if is_preflop:
                # Your preflop logic using evolved PARAMS
                hand_tier = self.preflop_tier(my_cards)
                if can_check:
                    if hand_tier == "premium":
                        raise_amt = min(int(state.big_blind * PARAMS["PREM_OPEN_MULT_MEAN"]), my_stack)
                        return max(raise_amt, state.big_blind * 2), memory
                    # ... rest of your preflop logic
                else:
                    # ... your facing bet logic
                    pass
            else:
                # Your postflop logic using evolved PARAMS
                hand_strength = self.get_hand_strength(my_cards)
                if can_check:
                    if hand_strength > PARAMS["POSTFLOP_BET_THRESHOLD"]:
                        bet_size = min(int(pot_size * 0.6), my_stack)
                        return max(bet_size, state.big_blind), memory
                    # ... rest of your postflop logic
                else:
                    # ... your facing bet logic
                    pass
                    
            return 0, memory  # Fallback
            
        except Exception as e:
            # Your error handling
            return 0, memory
    
    def preflop_tier(self, hole):
        # Include your preflop_tier_fixed logic
        return "premium"  # Simplified
    
    def get_hand_strength(self, hole):
        # Include your get_hand_strength_simple logic  
        return 0.5  # Simplified

BOT_CLASS = BotV3
'''

        with open('bots/bot_v3.py', 'w') as f:
            f.write(bot_v3_content)
        
        print("🤖 bots/bot_v3.py generated successfully!")

# Run overnight evolution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Overnight Poker Bot Evolution')
    parser.add_argument('--hours', type=float, default=8, help='Hours to run evolution')
    
    args = parser.parse_args()
    
    evolver = OvernightEvolver(total_hours=args.hours)
    evolver.run_overnight_evolution() 