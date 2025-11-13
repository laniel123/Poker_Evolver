# poker_debugger.py
import sys
import os
import inspect

# =============================================
# 🐛 POKER BOT DEBUGGING SUITE
# =============================================

class PokerDebugger:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.game_count = 0
        self.debug_log = []
        
    def log(self, message, level="INFO"):
        """Log debug messages"""
        entry = f"[{level}] {message}"
        self.debug_log.append(entry)
        if self.verbose:
            print(entry)
    
    def debug_game_state(self, game_state, bot_action, opponent_action, winner):
        """Debug individual game state"""
        self.game_count += 1
        self.log(f"🃏 Game {self.game_count}:", "DEBUG")
        self.log(f"   Bot Cards: {game_state.get('bot_cards', [])}", "DEBUG")
        self.log(f"   Opponent Cards: {game_state.get('opponent_cards', [])}", "DEBUG")
        self.log(f"   Community Cards: {game_state.get('community_cards', [])}", "DEBUG")
        self.log(f"   Bot Action: {bot_action}", "DEBUG")
        self.log(f"   Opponent Action: {opponent_action}", "DEBUG")
        self.log(f"   Winner: {winner}", "DEBUG")
        self.log(f"   Pot: {game_state.get('pot', 0)}", "DEBUG")
        self.log("---", "DEBUG")
        
        # Check for suspicious patterns
        self._check_suspicious_patterns(bot_action, opponent_action, winner)

    def debug_bot_decision(self, bot, game_state, bot_name):
        """Debug what action a bot is taking"""
        try:
            action = bot.get_action(game_state)
            self.log(f"🤖 {bot_name} decision:", "DEBUG")
            self.log(f"   Hand: {game_state.get('hand', [])}", "DEBUG")
            self.log(f"   Stack: {game_state.get('stack', 0)}", "DEBUG")
            self.log(f"   Pot: {game_state.get('pot', 0)}", "DEBUG")
            self.log(f"   Action chosen: {action}", "DEBUG")
            
            # Check if action is reasonable
            self._validate_action(action, bot_name, game_state)
            return action
        except Exception as e:
            self.log(f"❌ {bot_name} decision ERROR: {e}", "ERROR")
            return -1  # Fold on error

    def debug_hand_evaluation(self, hand1, hand2, community_cards, evaluate_hand_func):
        """Debug hand evaluation and comparison"""
        try:
            hand1_value = evaluate_hand_func(hand1 + community_cards)
            hand2_value = evaluate_hand_func(hand2 + community_cards)
            self.log(f"🃏 Hand Comparison:", "DEBUG")
            self.log(f"   Hand 1: {hand1} -> {hand1_value}", "DEBUG")
            self.log(f"   Hand 2: {hand2} -> {hand2_value}", "DEBUG")
            self.log(f"   Community: {community_cards}", "DEBUG")
            return hand1_value, hand2_value
        except Exception as e:
            self.log(f"❌ Hand evaluation ERROR: {e}", "ERROR")
            return None, None

    def validate_opponent_behavior(self, opponent_bot, game_state, opponent_name):
        """Test if opponents are making rational decisions"""
        test_state = game_state.copy()
        test_state['hand'] = ['Ah', 'Kh']  # Strong starting hand
        test_state['pot'] = 100
        test_state['stack'] = 1000
        
        try:
            action = opponent_bot.get_action(test_state)
            self.log(f"🧪 Opponent behavior test for {opponent_name}:", "TEST")
            self.log(f"   Strong hand: {test_state['hand']}", "TEST")
            self.log(f"   Opponent action: {action}", "TEST")
            
            if action in ['fold', -1]:
                self.log(f"🚨 WARNING: {opponent_name} folds with strong hand!", "WARNING")
            elif action in ['call', 'check', 0]:
                self.log(f"⚠️  NOTE: {opponent_name} calls/checks with strong hand", "TEST")
            else:
                self.log(f"✅ {opponent_name} raises/bets with strong hand - normal", "TEST")
                
        except Exception as e:
            self.log(f"❌ Behavior test ERROR for {opponent_name}: {e}", "ERROR")

    def debug_full_match(self, bot_v2, opponent_bot, match_num, opponent_name):
        """Debug a full match between bots"""
        self.log(f"\n🎲 MATCH {match_num} - {opponent_name}", "MATCH")
        self.log("="*50, "MATCH")

    def debug_bot_parameters(self, bot_instance, bot_name):
        """Debug a bot's current parameters"""
        self.log(f"🔧 {bot_name} Parameters:", "DEBUG")
        try:
            # Get all attributes that aren't methods or private
            params = {}
            for attr_name in dir(bot_instance):
                if not attr_name.startswith('_') and not callable(getattr(bot_instance, attr_name)):
                    attr_value = getattr(bot_instance, attr_name)
                    if isinstance(attr_value, (int, float, str, bool, list, dict)):
                        params[attr_name] = attr_value
            
            for param, value in params.items():
                self.log(f"   {param}: {value}", "DEBUG")
                
        except Exception as e:
            self.log(f"❌ Parameter debug ERROR: {e}", "ERROR")

    def _check_suspicious_patterns(self, bot_action, opponent_action, winner):
        """Check for patterns that indicate bugs"""
        # Check for always folding
        if opponent_action in ['fold', -1] and winner == "evolved":
            self.log("⚠️  Opponent folded - evolved wins", "PATTERN")
        
        # Check for unrealistic win patterns
        if self.game_count > 5:
            recent_wins = [entry for entry in self.debug_log[-10:] if "Winner: evolved" in entry]
            win_rate = len(recent_wins) / min(10, self.game_count)
            if win_rate > 0.9:
                self.log(f"🚨 SUSPICIOUS: {win_rate:.1%} win rate in last 10 games!", "WARNING")

    def _validate_action(self, action, bot_name, game_state):
        """Validate if a bot's action makes sense"""
        hand = game_state.get('hand', [])
        stack = game_state.get('stack', 0)
        pot = game_state.get('pot', 0)
        
        # Check if bot folds with strong hands
        if action in ['fold', -1] and hand:
            # Simple strength check - if high cards, folding might be suspicious
            high_cards = ['A', 'K', 'Q', 'J', '10']
            has_high_card = any(any(hc in card for card in hand) for hc in high_cards)
            if has_high_card and pot > stack * 0.1:  # Substantial pot
                self.log(f"⚠️  {bot_name} folds with potentially strong hand {hand}", "WARNING")

    def quick_win_rate_check(self, results, expected_max=0.8):
        """Quick check for unrealistic win rates"""
        for opponent, win_rate in results.items():
            if win_rate > expected_max:
                self.log(f"🚨 UNREALISTIC: {opponent} win rate: {win_rate:.1%}", "CRITICAL")
            elif win_rate > 0.7:
                self.log(f"⚠️  HIGH: {opponent} win rate: {win_rate:.1%}", "WARNING")
            else:
                self.log(f"✅ NORMAL: {opponent} win rate: {win_rate:.1%}", "INFO")

    def save_debug_log(self, filename="poker_debug_log.txt"):
        """Save debug log to file"""
        with open(filename, 'w') as f:
            for entry in self.debug_log:
                f.write(entry + '\n')
        self.log(f"💾 Debug log saved to {filename}", "INFO")

    def reset(self):
        """Reset the debugger state"""
        self.game_count = 0
        self.debug_log = []
        self.log("🔄 Debugger reset", "INFO")

# =============================================
# 🔧 INTEGRATION WITH YOUR EVOLVER
# =============================================

def create_debug_integration():
    """Create functions to integrate with your evolver"""
    
    def debug_simulate_game_wrapper(original_simulate_game):
        """Wrapper to add debugging to simulate_game"""
        def debug_wrapper(evolved_bot_instance, opponent_bot_instance, num_hands=15):
            debugger = PokerDebugger()
            
            debugger.log(f"🎯 Starting game simulation: {num_hands} hands", "GAME")
            debugger.debug_bot_parameters(evolved_bot_instance, "Evolved Bot")
            debugger.debug_bot_parameters(opponent_bot_instance, "Opponent Bot")
            
            # Test opponent behavior
            test_state = {
                'hand': ['Ah', 'Kh'],
                'stack': 1000,
                'pot': 100
            }
            debugger.validate_opponent_behavior(opponent_bot_instance, test_state, "Opponent")
            
            # Run original function
            win_rate = original_simulate_game(evolved_bot_instance, opponent_bot_instance, num_hands)
            
            debugger.log(f"🎯 Game finished - Win rate: {win_rate:.3f}", "GAME")
            
            if win_rate > 0.9:
                debugger.log("🚨 CRITICAL: Win rate > 90% - likely bug!", "CRITICAL")
            
            return win_rate
        
        return debug_wrapper
    
    def debug_test_strategy_wrapper(original_test_strategy):
        """Wrapper to add debugging to test_strategy_against_opponents"""
        def debug_wrapper(strategy, evolving_bot, opponents, bot_manager, tests_per_opponent=3):
            debugger = PokerDebugger()
            debugger.log(f"🧪 Testing strategy against {len(opponents)} opponents", "STRATEGY")
            
            # Run original function
            result = original_test_strategy(strategy, evolving_bot, opponents, bot_manager, tests_per_opponent)
            
            debugger.log(f"🧪 Strategy test complete - Fitness: {result:.3f}", "STRATEGY")
            
            if result > 0.8:
                debugger.log("🚨 CRITICAL: Strategy fitness > 0.8 - check for bugs!", "CRITICAL")
            
            return result
        
        return debug_wrapper
    
    return {
        'debug_simulate_game': debug_simulate_game_wrapper,
        'debug_test_strategy': debug_test_strategy_wrapper
    }

# =============================================
# 🚀 QUICK DEBUG MODE
# =============================================

def quick_debug_mode(bot_manager, opponent_name="balanced_bot"):
    """Run a quick debug session"""
    debugger = PokerDebugger()
    
    try:
        debugger.log("🚀 STARTING QUICK DEBUG MODE", "DEBUG")
        
        # Load bots
        evolved_bot = bot_manager.load_bot_instance("bot_v2_test")
        opponent_bot = bot_manager.load_bot_instance(opponent_name)
        
        debugger.log("🤖 Bots loaded successfully", "DEBUG")
        
        # Debug parameters
        debugger.debug_bot_parameters(evolved_bot, "bot_v2_test")
        debugger.debug_bot_parameters(opponent_bot, opponent_name)
        
        # Test behavior
        test_state = {
            'hand': ['Ah', 'Kh'],
            'stack': 1000,
            'pot': 100,
            'bot_cards': ['Ah', 'Kh'],
            'opponent_cards': ['2d', '7c'],
            'community_cards': []
        }
        
        debugger.validate_opponent_behavior(opponent_bot, test_state, opponent_name)
        
        # Test decisions
        debugger.log("🤖 Testing bot decisions...", "DEBUG")
        evolved_action = debugger.debug_bot_decision(evolved_bot, test_state, "bot_v2_test")
        opponent_action = debugger.debug_bot_decision(opponent_bot, test_state, opponent_name)
        
        debugger.log("✅ Quick debug completed", "DEBUG")
        debugger.save_debug_log("quick_debug_log.txt")
        
        return True
        
    except Exception as e:
        debugger.log(f"❌ Quick debug failed: {e}", "ERROR")
        return False

# =============================================
# 📊 USAGE EXAMPLES
# =============================================

if __name__ == "__main__":
    # Example usage
    debugger = PokerDebugger()
    
    # Test the debugger
    debugger.log("Testing debugger functionality", "INFO")
    
    # Example game state
    test_game_state = {
        'bot_cards': ['Ah', 'Kh'],
        'opponent_cards': ['Qd', 'Jd'], 
        'community_cards': ['10h', '9h', '2c'],
        'pot': 150
    }
    
    debugger.debug_game_state(test_game_state, "raise", "call", "evolved")
    
    # Save log
    debugger.save_debug_log()
    
    print("\n🎯 To integrate with your evolver:")
    print("1. Import PokerDebugger from this file")
    print("2. Create debugger instance: debugger = PokerDebugger()")
    print("3. Add debug calls to your simulate_game function")
    print("4. Run quick_debug_mode(bot_manager) to test basic functionality")