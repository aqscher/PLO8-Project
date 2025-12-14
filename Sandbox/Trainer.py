"""
train_ann.py - Training module for PLO8 Poker ANN
Implements self-play reinforcement learning
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
import random
import json
from datetime import datetime

import ANN
import GameController


class ReplayMemory:
    """Store and sample game experiences for training"""
    
    def __init__(self, capacity=10000):
        self.memory = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """Save an experience"""
        self.memory.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        """Sample a random batch of experiences"""
        return random.sample(self.memory, min(batch_size, len(self.memory)))
    
    def __len__(self):
        return len(self.memory)


class PokerTrainer:
    """
    Trainer for Poker ANN using self-play reinforcement learning
    """
    
    def __init__(self, model_path='poker_ann.pth'):
        self.ann = ANN.PokerANN()
        self.target_ann = ANN.PokerANN()  # Target network for stable training
        
        # The ANN already auto-loads poker_ann.pth if it exists in __init__
        # Just sync the target network with the main network
        self.target_ann.load_state_dict(self.ann.state_dict())
        
        # Training hyperparameters
        self.learning_rate = 0.001
        self.gamma = 0.99  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 64
        self.target_update_frequency = 100  # Update target network every N episodes
        
        # Optimizer and loss
        self.optimizer = optim.Adam(self.ann.parameters(), lr=self.learning_rate)
        
        # Replay memory
        self.memory = ReplayMemory(capacity=50000)
        
        # Training stats
        self.episode_rewards = []
        self.episode_count = 0
        
        print("Poker Trainer initialized")
        print(f"Learning rate: {self.learning_rate}")
        print(f"Gamma: {self.gamma}")
        print(f"Epsilon: {self.epsilon}")
    
    def select_action(self, game_state, player_seat, training=True):
        """
        Select action using epsilon-greedy policy
        
        Args:
            game_state: current game state
            player_seat: player making the decision
            training: if True, use epsilon-greedy; if False, use greedy
        
        Returns:
            action_str: selected action string
            action_idx: action index (0-4)
        """
        # Epsilon-greedy: explore vs exploit
        if training and random.random() < self.epsilon:
            # Random action (exploration)
            action_idx = random.randint(0, 4)
            action_str = self.ann.actions[action_idx]
        else:
            # Network decision (exploitation)
            input_vector = self.ann.process_state_to_input(game_state, player_seat)
            input_tensor = torch.FloatTensor(input_vector).unsqueeze(0)
            
            with torch.no_grad():
                action_probs = self.ann.forward(input_tensor)
                action_idx = torch.argmax(action_probs, dim=1).item()
                action_str = self.ann.actions[action_idx]
        
        return action_str, action_idx
    
    def calculate_reward(self, player_data, opponent_data, game_over, won_hand):
        """
        Calculate reward for the current state
        
        Args:
            player_data: player's data dict
            opponent_data: opponent's data dict
            game_over: bool, is the game over
            won_hand: bool, did player win this hand
        
        Returns:
            float: reward value
        """
        # Simple reward structure - customize as needed
        if game_over:
            if won_hand:
                return 10.0  # Won the hand
            else:
                return -10.0  # Lost the hand
        else:
            # Small reward for staying in the hand
            return 0.0
    
    def train_on_batch(self):
        """
        Train the network on a batch of experiences from replay memory
        """
        if len(self.memory) < self.batch_size:
            return 0.0
        
        # Sample batch from memory
        batch = self.memory.sample(self.batch_size)
        
        # Unpack batch
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(states))
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(np.array(next_states))
        dones = torch.FloatTensor(dones)
        
        # Current Q values
        current_q_values = self.ann(states)
        current_q_values = current_q_values.gather(1, actions.unsqueeze(1)).squeeze()
        
        # Next Q values from target network
        with torch.no_grad():
            next_q_values = self.target_ann(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Compute loss (Mean Squared Error)
        loss = nn.MSELoss()(current_q_values, target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def play_episode(self):
        """
        Play one full episode (hand) of poker for training
        
        Returns:
            float: total reward for the episode
        """
        # Initialize game
        settings = [2, 100.00, False]  # 2 players, 100bb stack, no human in loop
        controller = GameController.PLO8(settings)
        
        episode_reward = 0
        episode_experiences = []  # Store experiences for this episode
        
        # Track initial stacks to determine winner at end
        initial_stacks = {0: 100.0, 1: 100.0}
        
        # Play until hand is complete or game over
        step_count = 0
        max_steps = 100  # Prevent infinite loops
        
        while controller.running and controller.street < 4 and step_count < max_steps:
            # Get current state
            game_state = controller.get_game_state()
            
            # Check if we still have 2 players (game not over yet)
            if len(game_state['players']) < 2:
                break
            
            current_player = game_state['current_player']
            
            # Get current state encoding
            state_vector = self.ann.process_state_to_input(game_state, current_player)
            
            # Select action
            action_str, action_idx = self.select_action(game_state, current_player, training=True)
            
            # Store state and action for this step
            step_data = {
                'state': state_vector,
                'action': action_idx,
                'player': current_player
            }
            
            # Take action
            controller.advance_game(action_str)
            step_count += 1
            
            # Get next state
            next_game_state = controller.get_game_state()
            
            # Check if game ended (player eliminated)
            if len(next_game_state['players']) < 2 or controller.street >= 4:
                # Hand is over - assign rewards based on final stacks
                final_players = next_game_state['players']
                
                # Determine rewards for each player
                for exp in episode_experiences:
                    player_id = exp['player']
                    
                    # Find player's final stack
                    final_stack = 0.0
                    for p in final_players:
                        if p['seat'] == player_id:
                            final_stack = p['stack']
                            break
                    
                    # Calculate reward: profit/loss
                    profit = final_stack - initial_stacks[player_id]
                    reward = profit / 10.0  # Scale down the reward
                    
                    # Store experience with reward
                    dummy_next_state = np.zeros(114, dtype=np.float32)  # Terminal state
                    self.memory.push(exp['state'], exp['action'], reward, dummy_next_state, 1.0)
                    episode_reward += reward
                
                # Final experience for current step
                final_stack = 0.0
                for p in final_players:
                    if p['seat'] == current_player:
                        final_stack = p['stack']
                        break
                profit = final_stack - initial_stacks[current_player]
                reward = profit / 10.0
                
                dummy_next_state = np.zeros(114, dtype=np.float32)
                self.memory.push(step_data['state'], step_data['action'], reward, dummy_next_state, 1.0)
                episode_reward += reward
                
                break
            else:
                # Hand continues - store experience with 0 intermediate reward
                next_state_vector = self.ann.process_state_to_input(next_game_state, current_player)
                step_data['next_state'] = next_state_vector
                episode_experiences.append(step_data)
            
            # Train on batch periodically
            if len(self.memory) >= self.batch_size:
                loss = self.train_on_batch()
        
        return episode_reward
    
    def train(self, num_episodes=1000, save_frequency=100):
        """
        Train the network for a specified number of episodes
        
        Args:
            num_episodes: number of episodes to train
            save_frequency: save model every N episodes
        """
        print(f"\n{'='*60}")
        print(f"Starting training for {num_episodes} episodes")
        print(f"{'='*60}\n")
        
        for episode in range(num_episodes):
            # Play episode
            episode_reward = self.play_episode()
            self.episode_rewards.append(episode_reward)
            self.episode_count += 1
            
            # Decay epsilon
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
            
            # Update target network
            if episode % self.target_update_frequency == 0:
                self.target_ann.load_state_dict(self.ann.state_dict())
            
            # Logging
            if (episode + 1) % 10 == 0:
                avg_reward = np.mean(self.episode_rewards[-10:])
                print(f"Episode {episode + 1}/{num_episodes} | "
                      f"Avg Reward: {avg_reward:.2f} | "
                      f"Epsilon: {self.epsilon:.3f} | "
                      f"Memory: {len(self.memory)}")
            
            # Save model
            if (episode + 1) % save_frequency == 0:
                self.save_model(f'poker_ann_episode_{episode + 1}.pth')
                self.save_training_stats(f'training_stats_{episode + 1}.json')
        
        print(f"\n{'='*60}")
        print(f"Training complete!")
        print(f"{'='*60}\n")
        
        # Final save - save as both poker_ann.pth (for main.py) and poker_ann_final.pth (for backup)
        self.save_model('poker_ann.pth')
        self.save_model('poker_ann_final.pth')
        self.save_training_stats('training_stats_final.json')
    
    def save_model(self, filepath):
        """Save the model"""
        self.ann.save_model(filepath)
    
    def save_training_stats(self, filepath):
        """Save training statistics"""
        stats = {
            'episode_count': self.episode_count,
            'episode_rewards': self.episode_rewards,
            'epsilon': self.epsilon,
            'learning_rate': self.learning_rate,
            'gamma': self.gamma,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=4)
        
        print(f"Training stats saved to {filepath}")


# Main training script
if __name__ == "__main__":
    # Create trainer
    trainer = PokerTrainer()
    
    # Train
    trainer.train(num_episodes=10000, save_frequency=1000)
    
    print("\nTraining complete! Model saved to 'poker_ann_final.pth'")