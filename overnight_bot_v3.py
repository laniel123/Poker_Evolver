# overnight_bot_v3.py
import json
import time
import os
from datetime import datetime, timedelta

class OvernightBotV3Evolver:
    def __init__(self, total_hours=8):
        self.total_hours = total_hours
        self.start_time = time.time()
        self.end_time = self.start_time + (total_hours * 3600)
        self.results_dir = "overnight_results"
        os.makedirs(self.results_dir, exist_ok=True)
        
    def run_overnight_pipeline(self):
        """Run continuous evolution until time limit"""
        print("🌙 STARTING OVERNIGHT BOT_V3 EVOLUTION")
        print(f"⏰ Running for {self.total_hours} hours")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🕐 Will end: {(datetime.now() + timedelta(hours=self.total_hours)).strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        phase = 1
        overall_best = None
        overall_best_fitness = 0
        
        while time.time() < self.end_time:
            time_remaining = (self.end_time - time.time()) / 3600
            print(f"\n🕐 Time remaining: {time_remaining:.1f} hours")
            
            if phase == 1 and time_remaining > 6:
                print("🎯 PHASE 1: Foundation (3 hours)")
                best = self.run_timed_evolution(
                    opponents=["tight_bot", "loose_aggressive_bot", "calling_station_bot"],
                    hours=3,
                    phase_name="phase_1_foundation"
                )
                
            elif phase == 2 and time_remaining > 3:
                print("🎯 PHASE 2: Advanced (3 hours)")
                best = self.run_timed_evolution(
                    opponents=["smart_bot", "bluffing_bot"],
                    hours=3, 
                    phase_name="phase_2_advanced",
                    initial_strategy=overall_best
                )
                
            elif phase == 3 and time_remaining > 1:
                print("🎯 PHASE 3: Meta-Adaptation (2 hours)")
                best = self.run_timed_evolution(
                    opponents=self.get_all_opponents(),
                    hours=2,
                    phase_name="phase_3_meta",
                    initial_strategy=overall_best
                )
            
            else:
                # Final refinement with remaining time
                print(f"🎯 FINAL REFINEMENT ({time_remaining:.1f} hours)")
                best = self.run_timed_evolution(
                    opponents=self.get_all_opponents(),
                    hours=time_remaining,
                    phase_name="final_refinement", 
                    initial_strategy=overall_best
                )
            
            # Update overall best
            if best['fitness'] > overall_best_fitness:
                overall_best = best['strategy']
                overall_best_fitness = best['fitness']
                print(f"🔥 NEW OVERALL BEST: {overall_best_fitness:.3f}")
            
            phase += 1
            self.save_checkpoint(phase, overall_best, overall_best_fitness)
        
        # Create final bot_v3
        self.create_final_bot_v3(overall_best, overall_best_fitness)
        
    def run_timed_evolution(self, opponents, hours, phase_name, initial_strategy=None):
        """Run evolution for a specific time period"""
        from evolver import run_evolution
        
        end_time = time.time() + (hours * 3600)
        best_strategy = initial_strategy
        best_fitness = 0
        
        generation = 0
        while time.time() < end_time:
            generation += 1
            time_left = (end_time - time.time()) / 60  # minutes
            
            print(f"  Generation {generation} ({time_left:.1f}m remaining): ", end="")
            
            # Run one generation
            strategy, fitness = run_evolution(
                evolving_bot="bot_v2_test",
                opponents=opponents,
                generations=1,  # Run one generation at a time
                population_size=20,
                initial_population=[best_strategy] if best_strategy else None
            )
            
            if fitness > best_fitness:
                best_strategy = strategy
                best_fitness = fitness
                print(f"NEW BEST {fitness:.3f}")
            else:
                print(f"{fitness:.3f}")
            
            # Save progress every 5 generations
            if generation % 5 == 0:
                self.save_phase_progress(phase_name, generation, best_strategy, best_fitness)
        
        return {'strategy': best_strategy, 'fitness': best_fitness}
    
    def save_checkpoint(self, phase, strategy, fitness):
        """Save checkpoint so we can resume if interrupted"""
        checkpoint = {
            'phase': phase,
            'strategy': strategy,
            'fitness': fitness,
            'timestamp': datetime.now().isoformat(),
            'elapsed_hours': (time.time() - self.start_time) / 3600
        }
        
        filename = f"checkpoint_phase_{phase}.json"
        with open(os.path.join(self.results_dir, filename), 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        print(f"💾 Checkpoint saved: {filename}")
    
    def create_final_bot_v3(self, strategy, fitness):
        """Create the final bot_v3 after overnight evolution"""
        from bot_v3_generator import generate_bot_v3
        
        print("\n" + "=" * 70)
        print("🌅 OVERNIGHT EVOLUTION COMPLETE!")
        print(f"🏆 Final Fitness: {fitness:.3f}")
        print(f"🕐 Total time: {(time.time() - self.start_time) / 3600:.2f} hours")
        
        # Generate bot_v3
        generate_bot_v3(strategy)
        
        # Save final results
        final_results = {
            'final_strategy': strategy,
            'final_fitness': fitness,
            'total_evolution_hours': (time.time() - self.start_time) / 3600,
            'completion_time': datetime.now().isoformat()
        }
        
        with open(os.path.join(self.results_dir, "final_bot_v3_results.json"), 'w') as f:
            json.dump(final_results, f, indent=2)
        
        print("✅ bot_v3.py created with overnight-evolved strategies!")
        print("📊 Final results saved to overnight_results/")

# Run overnight
if __name__ == "__main__":
    evolver = OvernightBotV3Evolver(total_hours=8)  # 8 hours overnight
    evolver.run_overnight_pipeline()