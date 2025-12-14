"""
ANN.py - Artificial Neural Network for PLO8 poker decisions
Fully functional PyTorch implementation with 114-input architecture
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import os


class PokerANN(nn.Module):
    """
    PLO8 Poker Neural Network
    
    Architecture:
    - Input: 114 parameters
    - Hidden1: 256 neurons (ReLU)
    - Hidden2: 128 neurons (ReLU)
    - Hidden3: 64 neurons (ReLU)
    - Output: 5 neurons (Softmax)
    
    Input Encoding (114 total):
    - Player hole cards: 52 nodes (1-hot encoded)
    - Community cards: 52 nodes (1-hot encoded)
    - Current stack: 1 node (normalized 0-1)
    - Current bet size: 1 node (normalized 0-1)
    - Total pot: 1 node (normalized 0-1)
    - Betting street: 4 nodes (1-hot encoded: preflop, flop, turn, river)
    - Position: 1 node (0 or 1, dealer=1, non-dealer=0)
    - Adversary bet: 1 node (normalized 0-1)
    - Adversary stack: 1 node (normalized 0-1)
    """
    
    def __init__(self, input_size=114, hidden1=256, hidden2=128, hidden3=64, output_size=5):
        super(PokerANN, self).__init__()
        
        # Network layers
        self.fc1 = nn.Linear(input_size, hidden1)
        self.fc2 = nn.Linear(hidden1, hidden2)
        self.fc3 = nn.Linear(hidden2, hidden3)
        self.fc4 = nn.Linear(hidden3, output_size)
        
        # Action mapping
        self.actions = ['check/fold', 'call/minbet', 'bet1/2pot', 'bet3/4pot', 'betpot']
        
        # Card encoding mapping
        self.card_to_index = self._create_card_mapping()
        
        # Normalization constants
        self.max_stack = 200.0  # Assume max stack of 200bb for normalization
        self.max_pot = 400.0    # Assume max pot of 400bb for normalization
        
        print("Poker ANN initialized")
        print(f"Architecture: {input_size} -> {hidden1} -> {hidden2} -> {hidden3} -> {output_size}")
        print(f"Total parameters: {self.count_parameters()}")
        
        # Automatically load model if it exists
        if os.path.exists('poker_ann.pth'):
            self.load_model('poker_ann.pth')
        else:
            print("No saved model found. Using randomly initialized weights.")
    
    def forward(self, x):
        """Forward pass through the network"""
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        # Apply softmax to get action probabilities
        return F.softmax(x, dim=1)
    
    def count_parameters(self):
        """Count total trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def _create_card_mapping(self):
        """
        Create mapping from card string (e.g., 'HA', 'D10') to index (0-51)
        
        Order: C2-CA, D2-DA, S2-SA, H2-HA (52 cards)
        """
        suits = ['C', 'D', 'S', 'H']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        
        card_map = {}
        index = 0
        for suit in suits:
            for rank in ranks:
                card_str = suit + rank
                card_map[card_str] = index
                index += 1
        
        return card_map
    
    def encode_cards(self, cards):
        """
        Encode a list of cards as a 52-element 1-hot encoded vector
        
        Args:
            cards: list of card strings (e.g., ['HA', 'D10', 'CK', 'S2'])
        
        Returns:
            numpy array of shape (52,) with 1s at card positions
        """
        encoding = np.zeros(52, dtype=np.float32)
        
        for card in cards:
            if card and isinstance(card, str) and len(card) >= 2:
                # Handle the case where card might be None or invalid
                if card in self.card_to_index:
                    idx = self.card_to_index[card]
                    encoding[idx] = 1.0
        
        return encoding
    
    def encode_street(self, street):
        """
        Encode betting street as 4-element 1-hot vector
        
        Args:
            street: int (0=preflop, 1=flop, 2=turn, 3=river)
        
        Returns:
            numpy array of shape (4,)
        """
        encoding = np.zeros(4, dtype=np.float32)
        if 0 <= street <= 3:
            encoding[street] = 1.0
        return encoding
    
    def normalize_value(self, value, max_value):
        """
        Normalize a value to 0-1 range
        
        Args:
            value: float value to normalize
            max_value: maximum value for normalization
        
        Returns:
            float in range [0, 1]
        """
        return min(float(value) / max_value, 1.0)
    
    def process_state_to_input(self, game_state, player_seat):
        """
        Convert game state to 114-dimensional input vector
        
        Args:
            game_state: dict with game information
            player_seat: int (seat number of the player)
        
        Returns:
            numpy array of shape (114,)
        """
        input_vector = []
        
        # Get player and opponent data
        players = game_state['players']
        
        # Find current player
        current_player = None
        for p in players:
            if p['seat'] == player_seat:
                current_player = p
                break
        
        if current_player is None:
            # Player not found - return zero vector
            return np.zeros(114, dtype=np.float32)
        
        # Find opponent (assumes 2-player game)
        opponent = None
        for p in players:
            if p['seat'] != player_seat:
                opponent = p
                break
        
        # If no opponent (game over), use dummy values
        if opponent is None:
            opponent = {
                'seat': 1 - player_seat,
                'stack': 0.0,
                'bet': 0.0,
                'cards': [],
                'status': 'folded'
            }
        
        # 1. Player hole cards (52 nodes, 1-hot)
        hole_cards = current_player.get('cards', [])
        hole_encoding = self.encode_cards(hole_cards)
        input_vector.extend(hole_encoding)
        
        # 2. Community cards (52 nodes, 1-hot)
        community_cards = game_state.get('community_cards', [])
        community_encoding = self.encode_cards(community_cards)
        input_vector.extend(community_encoding)
        
        # 3. Current stack (1 node, normalized)
        stack = current_player.get('stack', 0)
        stack_norm = self.normalize_value(stack, self.max_stack)
        input_vector.append(stack_norm)
        
        # 4. Current bet size (1 node, normalized)
        current_bet = current_player.get('bet', 0)
        bet_norm = self.normalize_value(current_bet, self.max_stack)
        input_vector.append(bet_norm)
        
        # 5. Total pot (1 node, normalized)
        pot = game_state.get('pot', 0)
        pot_norm = self.normalize_value(pot, self.max_pot)
        input_vector.append(pot_norm)
        
        # 6. Betting street (4 nodes, 1-hot)
        street = game_state.get('street', 0)
        street_encoding = self.encode_street(street)
        input_vector.extend(street_encoding)
        
        # 7. Position (1 node, 0 or 1)
        dealer_position = game_state.get('dealer_position', 0)
        position = 1.0 if player_seat == dealer_position else 0.0
        input_vector.append(position)
        
        # 8. Adversary bet (1 node, normalized)
        opponent_bet = opponent.get('bet', 0)
        opp_bet_norm = self.normalize_value(opponent_bet, self.max_stack)
        input_vector.append(opp_bet_norm)
        
        # 9. Adversary stack (1 node, normalized)
        opponent_stack = opponent.get('stack', 0)
        opp_stack_norm = self.normalize_value(opponent_stack, self.max_stack)
        input_vector.append(opp_stack_norm)
        
        # Convert to numpy array and verify length
        input_array = np.array(input_vector, dtype=np.float32)
        
        if len(input_array) != 114:
            raise ValueError(f"Input vector has incorrect length: {len(input_array)} (expected 114)")
        
        return input_array
    
    def get_action(self, game_state, player_seat):
        """
        Analyze game state and return an action decision using the neural network
        
        Args:
            game_state: dict with game information
            player_seat: int (seat number of the player making decision)
        
        Returns:
            str: One of the valid actions:
                'check/fold', 'call/minbet', 'bet1/2pot', 'bet3/4pot', 'betpot'
        """
        # Process state to input vector
        input_vector = self.process_state_to_input(game_state, player_seat)
        
        # Convert to PyTorch tensor and add batch dimension
        input_tensor = torch.FloatTensor(input_vector).unsqueeze(0)  # Shape: (1, 114)
        
        # Forward pass through network
        with torch.no_grad():
            action_probs = self.forward(input_tensor)  # Shape: (1, 5)
        
        # Get action with highest probability
        action_idx = torch.argmax(action_probs, dim=1).item()
        action = self.actions[action_idx]
        
        # Optional: Print decision info
        probs = action_probs[0].numpy()
        print(f"ANN Player {player_seat} decision: {action}")
        print(f"  Action probabilities: {dict(zip(self.actions, probs))}")
        
        return action
    
    def get_action_distribution(self, game_state, player_seat):
        """
        Get the probability distribution over all actions (useful for training)
        
        Args:
            game_state: dict with game information
            player_seat: int (seat number of the player)
        
        Returns:
            dict: {action: probability}
        """
        input_vector = self.process_state_to_input(game_state, player_seat)
        input_tensor = torch.FloatTensor(input_vector).unsqueeze(0)
        
        with torch.no_grad():
            action_probs = self.forward(input_tensor)
        
        probs = action_probs[0].numpy()
        return dict(zip(self.actions, probs))
    
    def save_model(self, filepath='poker_ann.pth'):
        """
        Save model weights to file
        
        Args:
            filepath: path to save file
        """
        torch.save({
            'model_state_dict': self.state_dict(),
            'card_mapping': self.card_to_index,
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='poker_ann.pth'):
        """
        Load model weights from file
        
        Args:
            filepath: path to load file
        """
        if not os.path.exists(filepath):
            print(f"Model file {filepath} not found. Using randomly initialized weights.")
            return
        
        checkpoint = torch.load(filepath)
        self.load_state_dict(checkpoint['model_state_dict'])
        self.card_to_index = checkpoint['card_mapping']
        print(f"Model loaded from {filepath}")
    
    def train_step(self, states, actions, rewards, optimizer, criterion):
        """
        Perform a single training step
        
        Args:
            states: batch of state tensors (batch_size, 114)
            actions: batch of action indices (batch_size,)
            rewards: batch of rewards (batch_size,)
            optimizer: PyTorch optimizer
            criterion: loss function
        
        Returns:
            float: loss value
        """
        optimizer.zero_grad()
        
        # Forward pass
        action_probs = self.forward(states)
        
        # Calculate loss (example: policy gradient style)
        # You can customize this based on your training approach
        loss = criterion(action_probs, actions, rewards)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        return loss.item()


# Example usage and testing
if __name__ == "__main__":
    print("Testing Poker ANN...")
    
    # Create network
    ann = PokerANN()
    
    # Test with dummy game state
    test_state = {
        'players': [
            {
                'seat': 0,
                'stack': 100.0,
                'bet': 1.0,
                'cards': ['HA', 'HK', 'HQ', 'HJ'],
                'status': 'active'
            },
            {
                'seat': 1,
                'stack': 98.5,
                'bet': 1.0,
                'cards': ['CA', 'CK', 'CQ', 'CJ'],
                'status': 'active'
            }
        ],
        'street': 0,
        'pot': 2.0,
        'main_pot': 0.0,
        'side_pot': 0.0,
        'community_cards': [],
        'dealer_position': 0,
        'current_player': 0
    }
    
    # Test encoding
    print("\n--- Testing state encoding ---")
    input_vec = ann.process_state_to_input(test_state, 0)
    print(f"Input vector shape: {input_vec.shape}")
    print(f"Input vector length: {len(input_vec)}")
    print(f"First 10 elements: {input_vec[:10]}")
    
    # Test forward pass
    print("\n--- Testing forward pass ---")
    action = ann.get_action(test_state, 0)
    print(f"Selected action: {action}")
    
    # Test action distribution
    print("\n--- Testing action distribution ---")
    dist = ann.get_action_distribution(test_state, 0)
    for action, prob in dist.items():
        print(f"  {action}: {prob:.4f}")
    
    # Test save/load
    print("\n--- Testing save/load ---")
    ann.save_model('test_model.pth')
    
    ann2 = PokerANN()
    ann2.load_model('test_model.pth')
    print("Model loaded successfully")
    
    # Cleanup
    if os.path.exists('test_model.pth'):
        os.remove('test_model.pth')
    
    print("\n✓ All tests passed!")