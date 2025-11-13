# evolver.py
import json
import subprocess
import random
import statistics
import os
import importlib.util
import glob
from typing import Dict, List, Tuple
from datetime import datetime

# ===== CONFIGURATION =====
POPULATION_SIZE = 20
GENERATIONS = 50
TESTS_PER_OPPONENT = 2
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
        self.evolving_bot = "bot_v2_test"  # Default bot to evolve
    
    def discover_bots(self) -> Dict[str, str]:
        """Discover all bot files in the bots directory"""
        bots = {}
        bot_files = glob.glob(os.path.join(self.bots_dir, "*.py"))
        
        for bot_file in bot_files:
            bot_name = os.path.basename(bot_file)[:-3]  # Remove .py
            if bot_name != "__init__":
                bots[bot_name] = bot_file
                print(f"🤖 Found bot: {bot_name}")
        
        return bots
    
    def load_bot_class(self, bot_name: str):
        """Dynamically load a bot class from file"""
        if bot_name not in self.available_bots:
            raise ValueError(f"Bot '{bot_name}' not found")
        
        bot_file = self.available_bots[bot_name]
        spec = importlib.util.spec_from_file_location(bot_name, bot_file)
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)
        
        if hasattr(bot_module, 'BOT_CLASS'):
            return bot_module.BOT_CLASS
        else:
            raise AttributeError(f"Bot '{bot_name}' has no BOT_CLASS export")
    
    def set_evolving_bot(self, bot_name: str):
        """Set which bot to evolve"""
        if bot_name not in self.available_bots:
            raise ValueError(f"Bot '{bot_name}' not found")
        self.evolving_bot = bot_name
        print(f"🎯 Now evolving: {bot_name}")

    def get_evolving_bot_params(self) -> Dict:
        """Get the parameters for the evolving bot"""
        evolving_bot_file = self.available_bots[self.evolving_bot]
        
        # Read the file to extract PARAMS (simplified approach)
        # In practice, you might want a more robust parameter extraction
        with open(evolving_bot_file, 'r') as f:
            content = f.read()
        
        # This is a simple approach - you might want to improve this
        if "PARAMS = " in content:
            start = content.find("PARAMS = ") + len("PARAMS = ")
            end = content.find("\n", start)
            params_str = content[start:end].strip()
            try:
                return eval(params_str)
            except:
                return PARAM_RANGES.copy()
        else:
            return PARAM_RANGES.copy()

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
            mutation_size = (max_val - min_val) * 0.2
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
        if random.random() < 0.7:
            child[param] = parent1[param]
        else:
            child[param] = parent2[param]
    return child

def test_strategy_against_opponents(strategy: Dict, evolving_bot: str, opponents: List[str], 
                                  bot_manager: BotManager, tests_per_opponent: int = TESTS_PER_OPPONENT) -> float:
    """Test a strategy against multiple opponents"""
    print(f"Testing {evolving_bot} vs {len(opponents)} opponents: ", end="")
    
    # Save the strategy parameters
    evolved_params_file = "evolved_params.py"
    with open(evolved_params_file, 'w') as f:
        f.write(f"PARAMS = {json.dumps(strategy, indent=2)}\n")
    
    total_wins = 0
    total_games = 0
    
    for opponent in opponents:
        print(f"{opponent} ", end="")
        
        # Create simulation configuration
        config = {
            "player1_bot": evolving_bot,
            "player2_bot": opponent,
            "test_strategy": strategy
        }
        
        with open('simulation_config.json', 'w') as f:
            json.dump(config, f)
        
        wins = 0
        for i in range(tests_per_opponent):
            try:
                result = subprocess.run(
                    ['python3', 'poker_sim.py'],  # Your simulation runner
                    capture_output=True, 
                    text=True,
                    timeout=15
                )
                
                output = result.stdout
                # Check if evolving bot won
                if evolving_bot in output and "🏆 WINNER" in output:
                    winner_section = output.split("🏆 WINNER")[-1]
                    if evolving_bot in winner_section:
                        wins += 1
                
            except:
                pass
        
        total_wins += wins
        total_games += tests_per_opponent
    
    win_rate = total_wins / total_games if total_games > 0 else 0
    print(f"| Win rate: {win_rate:.3f}")
    
    return win_rate

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
    param_ranges = PARAM_RANGES  # You could make this bot-specific
    
    # Initialize population
    population = []
    for i in range(POPULATION_SIZE):
        strategy = generate_strategy(param_ranges)
        fitness = test_strategy_against_opponents(strategy, evolving_bot, opponents, bot_manager)
        population.append((strategy, fitness))
        print(f"Strategy {i+1}/{POPULATION_SIZE}: {fitness:.3f}")
    
    population.sort(key=lambda x: x[1], reverse=True)
    best_strategy, best_fitness = population[0]
    
    # Evolution loop
    for generation in range(GENERATIONS):
        print(f"\n🧬 Generation {generation + 1}/{GENERATIONS}")
        
        new_population = [population[0]]  # Elitism
        
        while len(new_population) < POPULATION_SIZE:
            # Tournament selection
            tournament = random.sample(population, 3)
            tournament.sort(key=lambda x: x[1], reverse=True)
            parent1, parent2 = tournament[0][0], tournament[1][0]
            
            # Create child
            if random.random() < 0.8:
                child = crossover_strategy(parent1, parent2, param_ranges)
            else:
                child = mutate_strategy(parent1, param_ranges)
            
            child = mutate_strategy(child, param_ranges)  # Always apply mutation
            
            fitness = test_strategy_against_opponents(child, evolving_bot, opponents, bot_manager)
            new_population.append((child, fitness))
        
        population = new_population
        population.sort(key=lambda x: x[1], reverse=True)
        
        current_best_strategy, current_best_fitness = population[0]
        
        if current_best_fitness > best_fitness:
            best_strategy = current_best_strategy
            best_fitness = current_best_fitness
            print(f"🔥 NEW BEST! Fitness: {best_fitness:.3f}")
    
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
    
    # Update the bot with best parameters
    evolved_params_file = "evolved_params.py"
    with open(evolved_params_file, 'w') as f:
        f.write(f"PARAMS = {json.dumps(best_strategy, indent=2)}\n")
    
    print("\n" + "=" * 60)
    print("🎉 EVOLUTION COMPLETE!")
    print(f"🏆 Best Fitness: {best_fitness:.3f}")
    print(f"💾 Results saved to: {results_file}")
    print(f"🤖 {evolving_bot} updated with best parameters")
    
    return best_strategy, best_fitness

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