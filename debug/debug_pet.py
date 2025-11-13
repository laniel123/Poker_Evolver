# debug_bet.py
import os
import importlib.util
import glob

def debug_bet_method():
    """Debug what the bet method actually returns"""
    bots_dir = "bots"
    bot_files = glob.glob(os.path.join(bots_dir, "*.py"))
    
    for bot_file in bot_files:
        bot_name = os.path.basename(bot_file)[:-3]
        if bot_name != "__init__" and not bot_name.startswith("evolved"):
            print(f"\n🔍 Debugging {bot_name}:")
            
            try:
                spec = importlib.util.spec_from_file_location(bot_name, bot_file)
                bot_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(bot_module)
                
                if hasattr(bot_module, 'BOT_CLASS'):
                    bot_class = bot_module.BOT_CLASS
                    bot_instance = bot_class()
                    
                    # Create a mock game state to test the bet method
                    from game_engine import GameState, Pot
                    
                    mock_state = GameState(
                        index_to_action=0,
                        index_of_small_blind=0,
                        players=["test_player"],
                        players_cards=["as", "ks"],  # Mock cards
                        held_money=[1000],
                        bet_money=[0],
                        community_cards=[],
                        pots=[Pot(0, ["test_player"])],
                        small_blind=10,
                        big_blind=20
                    )
                    
                    # Call the bet method and see what it returns
                    result = bot_instance.bet(mock_state)
                    print(f"   bet() returned: {result} (type: {type(result)})")
                    
                    # Check if it's a valid action for the game engine
                    if isinstance(result, (int, float)):
                        print(f"   ✅ Valid numeric action: {result}")
                    elif isinstance(result, tuple):
                        print(f"   ❌ Returns tuple: {result}")
                        print(f"   Expected: single integer (-1 for fold, 0 for check/call, >0 for raise)")
                    else:
                        print(f"   ❌ Unexpected return type: {type(result)}")
                        
                else:
                    print(f"   ❌ No BOT_CLASS found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_bet_method()