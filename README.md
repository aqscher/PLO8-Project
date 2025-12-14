# PLO8 Training Sandbox with Neural Network

A complete Pot Limit Omaha Hi-Lo (PLO8) poker training environment with a PyTorch-based neural network player.

## Architecture

### Neural Network Specifications

**Input Layer: 114 parameters**
- Player hole cards: 52 nodes (1-hot encoded)
- Community cards: 52 nodes (1-hot encoded)
- Current stack: 1 node (normalized 0-1)
- Current bet size: 1 node (normalized 0-1)
- Total pot: 1 node (normalized 0-1)
- Betting street: 4 nodes (1-hot encoded: preflop, flop, turn, river)
- Position: 1 node (0=non-dealer, 1=dealer)
- Adversary bet: 1 node (normalized 0-1)
- Adversary stack: 1 node (normalized 0-1)

**Hidden Layers:**
- Layer 1: 256 neurons (ReLU activation)
- Layer 2: 128 neurons (ReLU activation)
- Layer 3: 64 neurons (ReLU activation)

**Output Layer: 5 neurons (Softmax)**
- Maps to 5 possible actions:
  1. check/fold
  2. call/minbet
  3. bet1/2pot
  4. bet3/4pot
  5. betpot

**Total Parameters:** ~45,000 trainable parameters

## Installation

```bash
pip install -r requirements.txt
```

Requirements:
- Python 3.8+
- PyTorch 2.0+
- NumPy 1.24+
- Pygame 2.5+

## Usage

### 1. Play Against ANN (Human vs AI)

```python
# In main.py, set:
HUMAN_IN_LOOP = True

# Then run:
python main.py
```

You (Player 0) will use the UI buttons to make decisions. The ANN (Player 1) will make automatic decisions.

### 2. Watch ANN vs ANN

```python
# In main.py, set:
HUMAN_IN_LOOP = False

# Then run:
python main.py
```

Both players will be controlled by the neural network. Good for testing and observing learned behavior.

### 3. Train the ANN

```python
# Run the training script:
python train_ann.py
```

This will:
- Initialize the neural network with random weights
- Play episodes using self-play reinforcement learning
- Use epsilon-greedy exploration strategy
- Save checkpoints every 100 episodes
- Save final model to `poker_ann_final.pth`

Training hyperparameters (in `train_ann.py`):
- Learning rate: 0.001
- Discount factor (gamma): 0.99
- Epsilon decay: 0.995
- Batch size: 64
- Replay memory: 50,000 experiences

### 4. Load a Trained Model

The ANN automatically tries to load `poker_ann.pth` on initialization. To use a specific model:

```python
# In ANN.py __init__ or after initialization:
ann = ANN.PokerANN()
ann.load_model('poker_ann_episode_500.pth')
```

### 5. Test the Network

```python
# Test the network directly:
python -c "import ANN; ANN.PokerANN()"
```

Or run the built-in tests in ANN.py:
```python
python ANN.py
```

## File Structure

```
PLO8_Training_Sandbox/
├── main.py                 # Main game loop
├── GameController.py       # Game logic and state management
├── GameRenderer.py         # Pygame visualization
├── ANN.py                  # Neural network implementation
├── train_ann.py            # Training module
├── handEvaluator.py        # Hand evaluation (you need to provide this)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Game Controls

When playing as human (HUMAN_IN_LOOP = True):
- **CHECK / FOLD** - Check if possible, fold otherwise
- **CALL / BET MIN** - Call current bet or make minimum bet (1bb)
- **BET 1/2 POT** - Bet half the pot
- **BET 3/4 POT** - Bet three-quarters of the pot
- **BET POT** - Bet the full pot (pot limit)

**Perspective Slider:**
- Drag slider to change card visibility
- Position 0: See all cards (for analysis/training)
- Position 1-2: See only that player's cards (for playing)

## Customization

### Modify Network Architecture

Edit the `PokerANN.__init__()` in `ANN.py`:

```python
def __init__(self, input_size=114, hidden1=256, hidden2=128, hidden3=64, output_size=5):
    # Change hidden layer sizes as desired
```

### Adjust Training Parameters

Edit hyperparameters in `train_ann.py`:

```python
self.learning_rate = 0.001  # Learning rate
self.gamma = 0.99           # Discount factor
self.epsilon = 1.0          # Initial exploration rate
self.epsilon_decay = 0.995  # Exploration decay
self.batch_size = 64        # Training batch size
```

### Modify Reward Function

Edit `calculate_reward()` in `train_ann.py` to implement custom reward shaping:

```python
def calculate_reward(self, player_data, opponent_data, game_over, won_hand):
    # Customize reward structure here
    # Examples:
    # - Reward for pot size won
    # - Penalty for large losses
    # - Reward for aggressive play
    # - Reward for fold equity
```

### Change Game Settings

Edit settings in `main.py`:

```python
NUM_PLAYERS = 2              # Number of players (currently supports 2)
STARTING_STACK = 100.00      # Starting stack in big blinds
HUMAN_IN_LOOP = True         # True = Human vs AI, False = AI vs AI
```

## Training Tips

1. **Start with supervised learning**: Consider implementing imitation learning from expert play before pure RL
2. **Reward shaping**: Customize the reward function to encourage desired poker strategies
3. **Curriculum learning**: Start with simpler scenarios (e.g., post-flop only) before full games
4. **Population-based training**: Train against multiple versions of the network
5. **Track metrics**: Monitor win rate, average pot size, aggression frequency, etc.

## Advanced Features

### Save/Load Training Progress

```python
# Training stats are automatically saved to JSON files
# Load and analyze:
import json
with open('training_stats_final.json', 'r') as f:
    stats = json.load(f)
    
print(f"Total episodes: {stats['episode_count']}")
print(f"Final epsilon: {stats['epsilon']}")
```

### Analyze Action Distributions

```python
# Get probability distribution for a given state:
distribution = ann.get_action_distribution(game_state, player_seat)
for action, prob in distribution.items():
    print(f"{action}: {prob:.2%}")
```

### Export Model for Production

```python
# Save model in different format if needed:
torch.save(ann.state_dict(), 'model_weights_only.pth')

# Or export to ONNX for deployment:
dummy_input = torch.randn(1, 114)
torch.onnx.export(ann, dummy_input, 'poker_ann.onnx')
```

## Known Limitations

- Currently only supports 2-player heads-up play
- Showdown logic for 3+ players not implemented
- No tournament mode (only cash game)
- Fixed blind structure (0.5bb/1bb)
