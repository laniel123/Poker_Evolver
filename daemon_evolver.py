# daemon_evolver.py
import time
import json
import signal
import sys
import atexit

class DaemonEvolver:
    def __init__(self):
        self.running = True
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Handle graceful shutdown on CTRL+C"""
        def signal_handler(sig, frame):
            print(f"\n🛑 Received interrupt signal. Shutting down gracefully...")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Cleanup on exit
        atexit.register(self.cleanup)
    
    def cleanup(self):
        """Cleanup before exit"""
        print("🧹 Cleaning up before exit...")
    
    def run_indefinitely(self):
        """Run evolution until manually stopped"""
        print("🌀 DAEMON MODE: Running until stopped (CTRL+C to stop)")
        print("💡 This is perfect for weekend runs!")
        
        generation = 0
        best_fitness = 0
        
        while self.running:
            generation += 1
            print(f"\n🌀 Generation {generation}: ", end="")
            
            try:
                from evolver import run_evolution
                
                # Run one generation against all opponents
                strategy, fitness = run_evolution(
                    evolving_bot="bot_v2_test",
                    opponents=["tight_bot", "loose_aggressive_bot", "smart_bot", "bluffing_bot"],
                    generations=1,
                    population_size=25
                )
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    print(f"NEW BEST: {fitness:.3f}!")
                    
                    # Save new best strategy
                    with open('current_best_strategy.json', 'w') as f:
                        json.dump({'strategy': strategy, 'fitness': fitness}, f, indent=2)
                else:
                    print(f"Fitness: {fitness:.3f}")
                
                # Save progress every 10 generations
                if generation % 10 == 0:
                    self.save_progress(generation, best_fitness)
                    
                # Safety sleep to prevent overheating
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error in generation {generation}: {e}")
                time.sleep(5)  # Wait before retrying
    
    def save_progress(self, generation, fitness):
        """Save progress periodically"""
        progress = {
            'generation': generation,
            'best_fitness': fitness,
            'timestamp': datetime.now().isoformat()
        }
        
        with open('daemon_progress.json', 'w') as f:
            json.dump(progress, f, indent=2)
        
        print(f"💾 Progress saved (Generation {generation})")

# Run daemon mode
if __name__ == "__main__":
    daemon = DaemonEvolver()
    daemon.run_indefinitely()