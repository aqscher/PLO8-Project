"""
main.py - Entry point for PLO8 Training Sandbox
Connects GameController and GameRenderer
"""

#############################################################################
#                           CONTROL SETTINGS                                #

NUM_PLAYERS = 2
STARTING_STACK = 100.00
HUMAN_IN_LOOP = True
SETTINGS = [NUM_PLAYERS, STARTING_STACK, HUMAN_IN_LOOP]

#                                                                           #
#############################################################################

import GameController
import GameRenderer


def main(settings):
    """Main game loop - orchestrates controller and renderer"""
    
    # Initialize controller and renderer
    controller = GameController.PLO8(settings)
    renderer = GameRenderer.Render(settings)
    
    print("PLO8 Training Sandbox Started")
    print(f"Players: {NUM_PLAYERS}, Stack: {STARTING_STACK} bb")
    print("=" * 50)
    
    # Main game loop
    while controller.running:
        # 1. Get user input from renderer
        user_action = renderer.get_user_input()
        
        # 2. Quit or process action in controller
        if user_action:
            if user_action == 'quit':
                controller.running = False
                break
            else:
                controller.advance_game(user_action)
        
        # 3. Get current game state from controller
        game_state = controller.get_game_state()
        
        # 4. Render the state
        renderer.render(game_state)
    
    # Cleanup
    renderer.cleanup()
    print("Game ended")


if __name__ == "__main__":
    main(SETTINGS)


"""
### Architecture Overview

**Separation of Concerns:**
- Controller (GameController.py) never calls pygame functions
- Renderer (GameRenderer.py) never modifies game state directly
- Communication happens through immutable state objects

**State-Based Rendering:**
- Renderer is "dumb" - just draws what it's told
- Controller owns all game logic
- Makes testing much easier (test controller without graphics)

**Event Flow:**
1. User clicks button → Renderer captures event
2. Renderer returns action dict to main
3. Main passes action to Controller
4. Controller validates & processes action
5. Controller updates internal state
6. Main requests game state from Controller
7. Main passes state to Renderer
8. Renderer draws new state

**Benefits:**
- Easy to test game logic without graphics
- Could swap pygame for web UI, terminal, etc.
- Clear responsibility boundaries
- Easy to add AI players (just call controller methods)
- Can record/replay games by logging state changes
"""