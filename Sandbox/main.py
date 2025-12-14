"""
main.py - Entry point for PLO8 Training Sandbox
Connects GameController and GameRenderer
"""

#############################################################################
#                           CONTROL SETTINGS                                #

NUM_PLAYERS = 2
STARTING_STACK = 1000.00
HUMAN_IN_LOOP = True
SETTINGS = [NUM_PLAYERS, STARTING_STACK, HUMAN_IN_LOOP]

#                                                                           #
#############################################################################

import GameController
import GameRenderer
import ANN  # Import the ANN module


def main(settings):
    """Main game loop - orchestrates controller and renderer"""
    
    # Initialize controller and renderer
    controller = GameController.PLO8(settings)
    renderer = GameRenderer.Render(settings)
    
    # Initialize ANN
    ann = ANN.PokerANN()
    
    print("PLO8 Training Sandbox Started")
    print(f"Players: {NUM_PLAYERS}, Stack: {STARTING_STACK} bb")
    print(f"Mode: {'Human vs ANN' if HUMAN_IN_LOOP else 'ANN vs ANN'}")
    print("=" * 50)
    
    # Main game loop
    while controller.running:
        # Get current game state
        game_state = controller.get_game_state()
        current_player = game_state['current_player']
        
        # Determine who is acting
        action = None
        
        if HUMAN_IN_LOOP and current_player == 0:
            # Human player (Player 0) - get UI input
            action = renderer.get_user_input()
        else:
            # ANN player - get decision from neural network
            action = ann.get_action(game_state, current_player)
            
            # Still process UI events (for quit, window management, etc.)
            ui_event = renderer.get_user_input()
            if ui_event == 'quit':
                action = 'quit'
        
        # Process action in controller
        if action:
            if action == 'quit':
                controller.running = False
                break
            else:
                controller.advance_game(action)
        
        # Get updated game state
        game_state = controller.get_game_state()
        
        # Render the state
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
- ANN (ANN.py) only reads game state and returns actions
- Communication happens through immutable state objects

**State-Based Rendering:**
- Renderer is "dumb" - just draws what it's told
- Controller owns all game logic
- ANN reads state and returns action strings
- Makes testing much easier (test controller without graphics)

**Event Flow:**
1. Main determines who is acting (human or ANN)
2a. If human: User clicks button → Renderer captures event
2b. If ANN: ANN evaluates game state → Returns action
3. Main passes action to Controller
4. Controller validates & processes action
5. Controller updates internal state
6. Main requests game state from Controller
7. Main passes state to Renderer
8. Renderer draws new state

**Player Control Logic:**
- HUMAN_IN_LOOP = True:
  - Player 0: Human (UI input)
  - Player 1: ANN
- HUMAN_IN_LOOP = False:
  - Player 0: ANN
  - Player 1: ANN

**Benefits:**
- Easy to test game logic without graphics
- Could swap pygame for web UI, terminal, etc.
- Clear responsibility boundaries
- Easy to train AI players (just call ANN methods)
- Can record/replay games by logging state changes
- ANN can be swapped out or improved independently
"""