# evolver_final.py
import json
import random
import os
import importlib.util
import glob
from typing import Dict, List, Tuple
from datetime import datetime

# ===== CONFIGURATION =====
POPULATION_SIZE = 12
GENERATIONS = 25
TESTS_PER_OPPONENT = 3
BOTS_DIR = "bots"
RESULTS_DIR = "results"

# ===== PARAMETER RANGES FOR BOT_V2_TEST =====
PARAM_RANGES = {
    "PREM_OPEN_MULT_MEAN": (2.0, 6.0),
    "STRONG_OPEN_MULT_MEAN": (1.5, 4.0), 
    "MEDIUM_OPEN_FREQ": (0.1, 0.8),
    "MEDIUM_OPEN_MULT": (1.5, 3.5),
    "MEDIUM_CALL_CHEAP_FRAC": (0.05, 0.3),
    "POSTFLOP_BET_THRESHOLD": (0.3, 0.7),
    "POSTFLOP_BET_FREQ": (0.4, 0.9),
    "POSTFLOP_CALL_THRESHOLD": (0.2, 0.6),
    "POSTFLOP_CALL_POT_RATIO": (0.4, 0.8)
}

# ===== BOT MANAGEMENT =====
class BotManager:
    def __init__(self, bots_dir=BOTS_DIR):
        self.bots_dir = bots_dir
        self.available_bots = self.discover_bots()
        self.evolving_bot = "bot_v2_test"
    
    def discover_bots(self) -> Dict[str, str]:
        """Discover all bot files in the bots directory"""
        bots = {}
        bot_files = glob.glob(os.path.join(self.bots_dir, "*.py"))
        
        for bot_file in bot_files:
            bot_name = os.path.basename(bot_file)[:-3]
            if bot_name != "__init__" and not bot_name.startswith("evolved"):
                bots[bot_name] = bot_file
                print(f"🤖 Found bot: {bot_name}")
        
        return bots
    
    def load_bot_instance(self, bot_name: str):
        """Dynamically load and instantiate a bot"""
        if bot_name not in self.available_bots:
            raise ValueError(f"Bot '{bot_name}' not found")
        
        bot_file = self.available_bots[bot_name]
        spec = importlib.util.spec_from_file_location(bot_name, bot_file)
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)
        
        if hasattr(bot_module, 'BOT_CLASS'):
            return bot_module.BOT_CLASS()
        else:
            raise AttributeError(f"Bot '{bot_name}' has no BOT_CLASS export")
    
    def set_evolving_bot(self, bot_name: str):
        """Set which bot to evolve"""
        if bot_name not in self.available_bots:
            raise ValueError(f"Bot '{bot_name}' not found")
        self.evolving_bot = bot_name
        print(f"🎯 Now evolving: {bot_name}")

# ===== GAME SIMULATION =====
def extract_action_from_bet_result(bet_result):
    """Extract a valid action integer from whatever the bet method returns"""
    if bet_result is None:
        return -1  # Fold on None
    
    if isinstance(bet_result, (int, float)):
        # Already a number, return as int
        return int(bet_result)
    
    if isinstance(bet_result, tuple):
        # Handle tuple returns - take the first element
        if bet_result:
            first_element = bet_result[0]
            if isinstance(first_element, (int, float)):
                return int(first_element)
            elif first_element is None:
                return -1  # Fold on None as first element
        return -1  # Fold on empty tuple or invalid first element
    
    if isinstance(bet_result, str):
        # Handle string returns
        bet_result = bet_result.lower()
        if bet_result in ['fold', 'f']:
            return -1
        elif bet_result in ['check', 'call', 'c']:
            return 0
        else:
            # Try to extract number from string
            try:
                return int(bet_result)
            except:
                return -1
    
    # Default to fold for any other type
    return -1

def simulate_game(evolved_bot_instance, opponent_bot_instance, num_hands=15):
    """Run a full game simulation between two bots"""
    from game_engine import PokerGame
    
    # Create game instance
    game = PokerGame(
        player_names=["evolved", "opponent"],
        starting_stack=400,  # Small stacks for faster games
        sb=5,
        bb=10
    )
    
    evolved_wins = 0
    hands_played = 0
    
    while hands_played < num_hands and not game.game_over:
        # Get current game state for each player
        evolved_state = game.get_visible_state_for_player(0)
        opponent_state = game.get_visible_state_for_player(1)
        
        current_player = game.get_current_player()
        
        try:
            if current_player == "evolved":
                # Evolved bot's turn
                bet_result = evolved_bot_instance.bet(evolved_state)
                action = extract_action_from_bet_result(bet_result)
                result = game.apply_action(action)
            else:
                # Opponent bot's turn
                bet_result = opponent_bot_instance.bet(opponent_state)
                action = extract_action_from_bet_result(bet_result)
                result = game.apply_action(action)
        except Exception as e:
            # Default to fold on any error
            result = game.apply_action(-1)
        
        # Check if hand ended
        if game.game_over:
            if game.winner == "evolved":
                evolved_wins += 1
            break
        elif len(game.community_cards) == 5 and game.is_betting_round_complete():
            # Hand ended in showdown
            players_in = [i for i, name in enumerate(game.player_names) if name in game.pots[0].players]
            if len(players_in) == 2:
                # Compare hands at showdown
                from hand_evaluator import Hand
                evolved_hand = Hand(game.community_cards + game.players_cards[0])
                opponent_hand = Hand(game.community_cards + game.players_cards[1])
                
                if evolved_hand > opponent_hand:
                    evolved_wins += 1
                elif evolved_hand == opponent_hand:
                    # Split pot - count as 0.5 win
                    evolved_wins += 0.5
            elif len(players_in) == 1 and players_in[0] == 0:
                # Evolved won by fold
                evolved_wins += 1
            
            hands_played += 1
            if hands_played < num_hands and not game.game_over:
                game.start_new_hand()
    
    win_rate = evolved_wins / max(hands_played, 1)
    return win_rate

# ===== EVOLUTION FUNCTIONS =====
def generate_strategy(param_ranges: Dict) -> Dict:
    """Generate a random strategy within parameter ranges"""
    strategy = {}
    for param, (min_val, max_val) in param_ranges.items():
        if param.endswith(('_FREQ', '_FRAC', '_THRESHOLD', '_RATIO')):
            strategy[param] = round(random.uniform(min_val, max_val), 3)
        else:
            strategy[param] = round(random.uniform(min_val, max_val), 2)
    return strategy

def mutate_strategy(strategy: Dict, param_ranges: Dict, mutation_rate: float = 0.3) -> Dict:
    """Mutate a strategy with controlled randomness"""
    mutated = strategy.copy()
    for param, (min_val, max_val) in param_ranges.items():
        if random.random() < mutation_rate:
            current = mutated[param]
            mutation_size = (max_val - min_val) * 0.1
            new_val = current + random.uniform(-mutation_size, mutation_size)
            new_val = max(min_val, min(max_val, new_val))
            
            if param.endswith(('_FREQ', '_FRAC', '_THRESHOLD', '_RATIO')):
                mutated[param] = round(new_val, 3)
            else:
                mutated[param] = round(new_val, 2)
    return mutated

def crossover_strategy(parent1: Dict, parent2: Dict, param_ranges: Dict) -> Dict:
    """Combine two strategies to create a child"""
    child = {}
    for param in param_ranges.keys():
        if random.random() < 0.5:
            child[param] = parent1[param]
        else:
            child[param] = parent2[param]
    return child

def create_evolved_bot_instance(strategy: Dict, base_bot_name: str, bot_manager: BotManager):
    """Create an instance of the evolved bot with the given strategy"""
    # Load the base bot class
    base_bot_file = bot_manager.available_bots[base_bot_name]
    spec = importlib.util.spec_from_file_location(base_bot_name, base_bot_file)
    base_bot_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base_bot_module)
    
    base_bot_class = base_bot_module.BOT_CLASS
    
    # Create a new class that inherits from the base bot but uses evolved parameters
    class EvolvedBot(base_bot_class):
        def __init__(self):
            super().__init__()
            # Override with evolved parameters
            for param, value in strategy.items():
                if hasattr(self, param):
                    setattr(self, param, value)
    
    return EvolvedBot()

def test_strategy_against_opponents(strategy: Dict, evolving_bot: str, opponents: List[str], 
                                  bot_manager: BotManager, tests_per_opponent: int = TESTS_PER_OPPONENT) -> float:
    """Test a strategy against multiple opponents using real game engine"""
    print(f"Testing {evolving_bot} vs {len(opponents)} opponents: {', '.join(opponents)}")
    
    total_win_rate = 0
    opponent_count = 0
    
    for opponent in opponents:
        try:
            print(f"   🎮 vs {opponent}: ", end="")
            # Create bot instances
            evolved_bot = create_evolved_bot_instance(strategy, evolving_bot, bot_manager)
            opponent_bot = bot_manager.load_bot_instance(opponent)
            
            # Run multiple games against this opponent
            opponent_wins = 0
            for game_num in range(tests_per_opponent):
                win_rate = simulate_game(evolved_bot, opponent_bot)
                opponent_wins += win_rate
                print(f"{win_rate:.2f} ", end="")
            
            avg_win_rate = opponent_wins / tests_per_opponent
            total_win_rate += avg_win_rate
            opponent_count += 1
            print(f"(avg: {avg_win_rate:.3f})")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    final_win_rate = total_win_rate / opponent_count if opponent_count > 0 else 0
    print(f"   📊 Overall win rate: {final_win_rate:.3f}")
    
    return final_win_rate

# ===== MAIN EVOLUTION =====
def run_evolution(evolving_bot: str = "bot_v2_test", opponents: List[str] = None):
    """Run evolution for a specific bot against specified opponents"""
    
    # Create results directory
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    bot_manager = BotManager()
    bot_manager.set_evolving_bot(evolving_bot)
    
    # Use all other bots as opponents if none specified
    if opponents is None:
        opponents = [bot for bot in bot_manager.available_bots.keys() if bot != evolving_bot]
    
    print("🚀 MODULAR POKER EVOLVER")
    print("=" * 60)
    print(f"Evolving bot: {evolving_bot}")
    print(f"Testing against: {', '.join(opponents)}")
    print(f"Population: {POPULATION_SIZE}, Generations: {GENERATIONS}")
    print("=" * 60)
    
    # Get parameter ranges for the evolving bot
    param_ranges = PARAM_RANGES
    
    # Initialize population
    population = []
    print("\n🧬 Initializing population...")
    for i in range(POPULATION_SIZE):
        strategy = generate_strategy(param_ranges)
        print(f"\nStrategy {i+1}/{POPULATION_SIZE}:")
        fitness = test_strategy_against_opponents(strategy, evolving_bot, opponents, bot_manager)
        population.append((strategy, fitness))
        print(f"   Fitness: {fitness:.3f}")
    
    population.sort(key=lambda x: x[1], reverse=True)
    best_strategy, best_fitness = population[0]
    
    # Evolution loop
    for generation in range(GENERATIONS):
        print(f"\n🧬 Generation {generation + 1}/{GENERATIONS}")
        
        new_population = [population[0]]  # Elitism - keep the best
        
        while len(new_population) < POPULATION_SIZE:
            # Tournament selection
            tournament = random.sample(population, min(3, len(population)))
            tournament.sort(key=lambda x: x[1], reverse=True)
            parent1, parent2 = tournament[0][0], tournament[1][0]
            
            # Create child
            if random.random() < 0.8:  # 80% crossover, 20% mutation only
                child = crossover_strategy(parent1, parent2, param_ranges)
            else:
                child = parent1.copy()  # Start with parent1
            
            # Always apply some mutation
            child = mutate_strategy(child, param_ranges, mutation_rate=0.4)
            
            fitness = test_strategy_against_opponents(child, evolving_bot, opponents, bot_manager)
            new_population.append((child, fitness))
        
        population = new_population
        population.sort(key=lambda x: x[1], reverse=True)
        
        current_best_strategy, current_best_fitness = population[0]
        
        if current_best_fitness > best_fitness:
            best_strategy = current_best_strategy
            best_fitness = current_best_fitness
            print(f"🔥 NEW BEST! Fitness: {best_fitness:.3f}")
        
        # Early stopping if we're doing well
        if best_fitness > 0.6 and generation > 10:
            print(f"🏆 Early stopping - achieved good fitness!")
            break
    
    # Save final results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(RESULTS_DIR, f"evolution_{evolving_bot}_{timestamp}.json")
    
    with open(results_file, 'w') as f:
        json.dump({
            "evolving_bot": evolving_bot,
            "opponents": opponents,
            "best_fitness": best_fitness,
            "best_strategy": best_strategy,
            "timestamp": timestamp,
            "generations": GENERATIONS,
            "population_size": POPULATION_SIZE
        }, f, indent=2)
    
    # Create the final evolved bot file
    final_bot_content = generate_evolved_bot_code(best_strategy, evolving_bot, bot_manager)
    final_bot_file = f"bots/evolved_{evolving_bot}_{timestamp}.py"
    
    with open(final_bot_file, 'w') as f:
        f.write(final_bot_content)
    
    print("\n" + "=" * 60)
    print("🎉 EVOLUTION COMPLETE!")
    print(f"🏆 Best Fitness: {best_fitness:.3f}")
    print(f"💾 Results saved to: {results_file}")
    print(f"🤖 Evolved bot saved to: {final_bot_file}")
    
    return best_strategy, best_fitness

def generate_evolved_bot_code(strategy: Dict, base_bot_name: str, bot_manager: BotManager) -> str:
    """Generate Python code for the evolved bot"""
    base_bot_file = bot_manager.available_bots[base_bot_name]
    
    # Read the base bot
    with open(base_bot_file, 'r') as f:
        base_code = f.read()
    
    # Create evolved bot code by replacing parameter assignments
    lines = base_code.split('\n')
    final_lines = []
    
    for line in lines:
        # Check if this line sets one of our parameters
        param_set = False
        for param in strategy.keys():
            if f"self.{param} =" in line and not line.strip().startswith('#'):
                # Replace with evolved value
                final_lines.append(f"        self.{param} = {strategy[param]}  # Evolved")
                param_set = True
                break
        
        if not param_set:
            final_lines.append(line)
    
    # Add evolution info at the top
    final_code = f'"""\nEvolved version of {base_bot_name}\nGenerated by genetic algorithm on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nBest fitness: {max(0, 0):.3f}\n"""\n\n' + '\n'.join(final_lines)
    
    return final_code

# ===== COMMAND LINE INTERFACE =====
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Modular Poker Bot Evolver')
    parser.add_argument('--evolve', type=str, help='Bot to evolve (default: bot_v2_test)')
    parser.add_argument('--against', nargs='+', help='Opponents to test against')
    parser.add_argument('--list-bots', action='store_true', help='List available bots')
    
    args = parser.parse_args()
    
    bot_manager = BotManager()
    
    if args.list_bots:
        print("🤖 Available Bots:")
        for bot_name in bot_manager.available_bots.keys():
            print(f"  - {bot_name}")
    else:
        evolving_bot = args.evolve or "bot_v2_test"
        opponents = args.against
        
        run_evolution(evolving_bot, opponents)