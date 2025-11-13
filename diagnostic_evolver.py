# diagnostic_evolver.py
import os
import importlib.util
import glob

def diagnose_bot_methods():
    """Check what methods are available in the bots"""
    bots_dir = "bots"
    bot_files = glob.glob(os.path.join(bots_dir, "*.py"))
    
    for bot_file in bot_files:
        bot_name = os.path.basename(bot_file)[:-3]
        if bot_name != "__init__" and not bot_name.startswith("evolved"):
            print(f"\n🔍 Analyzing {bot_name}:")
            
            try:
                spec = importlib.util.spec_from_file_location(bot_name, bot_file)
                bot_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(bot_module)
                
                if hasattr(bot_module, 'BOT_CLASS'):
                    bot_class = bot_module.BOT_CLASS
                    bot_instance = bot_class()
                    
                    print(f"   Class: {bot_class.__name__}")
                    print(f"   Methods: {[method for method in dir(bot_instance) if not method.startswith('_')]}")
                    
                    # Check for common decision-making methods
                    decision_methods = ['make_decision', 'bet', 'action', 'play', 'decide', 'get_action']
                    for method in decision_methods:
                        if hasattr(bot_instance, method):
                            print(f"   ✅ Found potential decision method: {method}")
                            
                else:
                    print(f"   ❌ No BOT_CLASS found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    diagnose_bot_methods()