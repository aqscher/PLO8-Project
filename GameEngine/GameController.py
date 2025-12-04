"""
GameController.py - Game logic and state management for PLO8 poker
Handles all game rules, betting, hand evaluation, and state transitions
"""

import random
import json
from decimal import Decimal, getcontext, ROUND_HALF_UP

# Decimal configuration
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP
CENTS = Decimal("0.01")

class PLO8:
    def __init__(self, settings):
        """Initialize game controller with settings"""
        # Settings
        self.starting_players = settings[0]
        self.starting_stack = settings[1]
        self.human_in_loop = settings[2]
        
        # Game state
        self.players = []
        self.street = 0     #Street int: 0: Preflop, 1:Flop, 2:Turn, 3:River, 4:Showdown
        self.pot = Decimal("0.00")    # total pot
        self.main_pot = Decimal("0.00")   # main pot
        self.side_pot = Decimal("0.00")   # side pot
        self.side_pot1 = Decimal("0.00")   # side pot +1
        self.side_pot2 = Decimal("0.00")   # side pot +2
        self.side_pot3 = Decimal("0.00")   # side pot +3
        self.side_pot4 = Decimal("0.00")   # side pot +4
        self.side_pot5 = Decimal("0.00")   # side pot +5
        self.side_pot6 = Decimal("0.00")   # side pot +6
        self.side_pot7 = Decimal("0.00")   # side pot +7
        self.community_cards = []
        self.dealer_position = 0
        self.current_player = 0

        self.running = True
        self.init_game()
        self.new_hand()
    
    def q(self, value):
        """Quantize a Decimal value to cents."""
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        return value.quantize(CENTS)

    def init_game(self):
        """Initialize a new game"""
        # Create players
        self.players = []
        for i in range(self.starting_players):
            player = {
                'seat': i,
                'stack': Decimal(str(self.starting_stack+i)),
                'bet': Decimal("0.00"),
                'status': 'active',     # active, folded 
                'cards': [None, None, None, None],  # 4 hole cards for PLO8
                'acted': False,
                'allin': False,
                'contrib': Decimal("0.00")
            }
            self.players.append(player)
        
        # Random dealer position
        self.dealer_position = random.randint(0, self.starting_players-1)
        print(f"Game initialized: {self.starting_players} players, dealer at seat {self.dealer_position}")

    def new_hand(self):
        # Eject the brokies
        self.players = [p for p in self.players if p['stack'] != Decimal("0.00")]
        if len(self.players) < 2:
            print("Not enough players to start a new hand. Game Over.")
            self.running = False
            return

        # Reset pot, street, update dealer position, deal new cards, reset player flags, community cards
        self.pot, self.main_pot, self.side_pot = Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
        self.side_pot1, self.side_pot2, self.side_pot3 = Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
        self.side_pot4, self.side_pot5, self.side_pot6, self.side_pot7 = Decimal("0.00"), Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
        self.street = 0
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        self.community_cards = []
        self.init_deck()
        for player in self.players:
            player['bet'] = Decimal("0.00")
            player['status'] = 'active'
            player['cards'] = [self.deal_card(), self.deal_card(), self.deal_card(), self.deal_card()]
            player['acted'] = False
            player['allin'] = False
            player['contrib'] = Decimal("0.00")   # reset contribution for new hand
        
        # 2 Player blinds set up
        if len(self.players) == 2:
            #small blind
            sb_idx = self.dealer_position % len(self.players)
            bb_idx = (self.dealer_position+1) % len(self.players)

            if self.players[sb_idx]['stack'] > Decimal("0.50"):
                self.players[sb_idx]['stack'] -= Decimal("0.50")
                self.players[sb_idx]['bet'] = Decimal("0.50")
                self.players[sb_idx]['contrib'] += Decimal("0.50")
                self.pot += Decimal("0.50")
            else:
                # all-in small blind
                added = self.players[sb_idx]['stack']
                self.players[sb_idx]['bet'] = added
                self.players[sb_idx]['contrib'] += added
                self.players[sb_idx]['stack'] = Decimal("0.00")
                self.players[sb_idx]['allin'] = True
                self.pot += added

            #big blind    
            if self.players[bb_idx]['stack'] > Decimal("1.00"):
                self.players[bb_idx]['stack'] -= Decimal("1.00")
                self.players[bb_idx]['bet'] = Decimal("1.00")
                self.players[bb_idx]['contrib'] += Decimal("1.00")
                self.pot += Decimal("1.00")
            else:
                added = self.players[bb_idx]['stack']
                self.players[bb_idx]['bet'] = added
                self.players[bb_idx]['contrib'] += added
                self.players[bb_idx]['stack'] = Decimal("0.00")
                self.players[bb_idx]['allin'] = True
                self.pot += added

            self.current_player = self.dealer_position
            return

        # 3+ Player blinds set up
        sb_idx = (self.dealer_position+1) % len(self.players)
        bb_idx = (self.dealer_position+2) % len(self.players)

        #small blind
        if self.players[sb_idx]['stack'] > Decimal("0.50"):
            self.players[sb_idx]['stack'] -= Decimal("0.50")
            self.players[sb_idx]['bet'] = Decimal("0.50")
            self.players[sb_idx]['contrib'] += Decimal("0.50")
            self.pot += Decimal("0.50")
        else:
            added = self.players[sb_idx]['stack']
            self.players[sb_idx]['bet'] = added
            self.players[sb_idx]['contrib'] += added
            self.players[sb_idx]['stack'] = Decimal("0.00")
            self.players[sb_idx]['allin'] = True
            self.pot += added
        #big blind
        if self.players[bb_idx]['stack'] > Decimal("1.00"):
            self.players[bb_idx]['stack'] -= Decimal("1.00")
            self.players[bb_idx]['bet'] = Decimal("1.00")
            self.players[bb_idx]['contrib'] += Decimal("1.00")
            self.pot += Decimal("1.00")
        else:
            added = self.players[bb_idx]['stack']
            self.players[bb_idx]['bet'] = added
            self.players[bb_idx]['contrib'] += added
            self.players[bb_idx]['stack'] = Decimal("0.00")
            self.players[bb_idx]['allin'] = True
            self.pot += added

        self.current_player = (self.dealer_position + 3) % len(self.players)


    def get_game_state(self):
        """
        Return current game state for rendering
        Returns dict with all necessary display information
        """
        # Convert Decimals to floats for JSON serialization / display
        players_copy = []
        for p in self.players:
            p_copy = p.copy()
            # convert stack, bet, and contrib to float for JSON
            if isinstance(p_copy.get('stack'), Decimal):
                p_copy['stack'] = float(self.q(p_copy['stack']))
            if isinstance(p_copy.get('bet'), Decimal):
                p_copy['bet'] = float(self.q(p_copy['bet']))
            if isinstance(p_copy.get('contrib'), Decimal):
                p_copy['contrib'] = float(self.q(p_copy['contrib']))
            players_copy.append(p_copy)

        return {
            'players': players_copy,
            'street': self.street,
            'pot': float(self.q(self.pot)),
            'main_pot': float(self.q(self.main_pot)),
            'side_pot': float(self.q(self.side_pot)),
            'side_pot1': float(self.q(self.side_pot1)),
            'side_pot2': float(self.q(self.side_pot2)),
            'side_pot3': float(self.q(self.side_pot3)),
            'side_pot4': float(self.q(self.side_pot4)),
            'side_pot5': float(self.q(self.side_pot5)),
            'side_pot6': float(self.q(self.side_pot6)),
            'community_cards': self.community_cards,
            'dealer_position': self.dealer_position,
            'current_player': self.current_player
        }

    # -------------------------
    # New pot-building utilities
    # -------------------------
    def build_pots(self):
        """
        Build main pot + side pots from player['contrib'] values.
        Returns a list of pots in ascending order of cap:
          pots[0] is main pot (lowest cap), each pot is dict:
            {'amount': Decimal, 'eligible': [player_dicts]}
        """
        # collect unique positive contribution levels, sorted ascending
        levels = sorted({p['contrib'] for p in self.players if p['contrib'] > 0})
        if not levels:
            return []

        pots = []
        prev = Decimal("0.00")

        # for each level, compute the pot slice and eligible players
        for level in levels:
            pot_amount = Decimal("0.00")
            eligible = []

            for p in self.players:
                contrib = p['contrib']
                # amount this player contributes to this level
                if contrib > prev:
                    pay_in = min(contrib, level) - prev
                    if pay_in > 0:
                        pot_amount += pay_in

                # a player is eligible for this pot if they contributed at least 'level'
                # and they have not folded (folded players cannot win)
                if contrib >= level and p['status'] == 'active':
                    eligible.append(p)

            pots.append({"amount": self.q(pot_amount), "eligible": eligible})
            prev = level

        return pots

    def clear_pots_fields(self, pots):
        """
        Map built pots to self.main_pot and side_pot, side_pot1... for debugging/display.
        pots should be ordered lowest->highest contribution tier.
        """
        # reset fields
        self.main_pot = Decimal("0.00")
        self.side_pot = Decimal("0.00")
        self.side_pot1 = Decimal("0.00")
        self.side_pot2 = Decimal("0.00")
        self.side_pot3 = Decimal("0.00")
        self.side_pot4 = Decimal("0.00")
        self.side_pot5 = Decimal("0.00")
        self.side_pot6 = Decimal("0.00")
        self.side_pot7 = Decimal("0.00")

        # map
        field_order = ['main_pot', 'side_pot', 'side_pot1', 'side_pot2', 'side_pot3', 'side_pot4', 'side_pot5', 'side_pot6', 'side_pot7']
        for i, pot in enumerate(pots):
            if i >= len(field_order):
                break
            setattr(self, field_order[i], pot['amount'])

    def payout_pots(self, pots, winners_by_rank):
        """
        Distribute pot amounts to winners.
        pots: list of {'amount': Decimal, 'eligible': [player_dicts]}
        winners_by_rank: list of lists of player dicts, in rank order (best first).
            Example: [[p1], [p2,p3], [p4]]  -> p1 best, p2&p3 tied for 2nd, etc.
        """
        for pot in pots:
            amt = pot['amount']
            eligible = set(pot['eligible'])

            # find the best-ranked winner(s) who are eligible
            winner_group = None
            for rank_group in winners_by_rank:
                group = [p for p in rank_group if p in eligible]
                if group:
                    winner_group = group
                    break

            if not winner_group:
                # no eligible winner (all folded?) — skip
                continue

            share = (amt / Decimal(len(winner_group))).quantize(CENTS)

            # Distribute shares — if rounding leftover exists, give remainder to earliest seat in winner_group
            total_distributed = share * Decimal(len(winner_group))
            remainder = amt - total_distributed

            for w in winner_group:
                w['stack'] += share

            if remainder > 0:
                # choose winner with smallest seat index to receive remainder
                winner_group_sorted = sorted(winner_group, key=lambda x: x['seat'])
                winner_group_sorted[0]['stack'] += remainder

    # Main loop from here
    def advance_game(self, action):
        if self.street == 4:
            self.new_hand()
            return
        if len(self.players) == 1:
            print("Game Over!")
            self.running = False
            return
        #get player action, check to see if game over
        self.process_action(action)
        
        #handle end of hand where all but 1 player folds
        if sum(1 for player in self.players if player['status'] == 'active') == 1 and self.street < 4:
            winner = next((player for player in self.players if player['status'] == 'active'), None)
            if winner == None:
                raise Exception("Winner is none.")
            winner['stack'] += self.q(self.pot)
            print(f"Player {winner['seat']} wins the hand, starting new hand...")
            self.new_hand()
            return
        
        # NEW: Check if betting should end due to all-in situations
        action_players = [p for p in self.players if p['status'] == 'active' and not p['allin']]
        
        # If 0 or 1 players can still act, advance to next street
        if len(action_players) <= 1:
            # If there's exactly 1 player who can act, they need to match the highest bet first
            if len(action_players) == 1:
                solo_player = action_players[0]
                max_bet = max(p['bet'] for p in self.players)
                # If the solo player hasn't matched the bet yet and hasn't acted, let them act
                if solo_player['bet'] < max_bet and not solo_player['acted']:
                    self.current_player = solo_player['seat']
                    return
            
            # Otherwise, everyone is all-in or only one player left who has already acted
            print("All players are all-in or have acted, advancing streets to showdown...")
            while self.street < 4:
                self.new_street()
            self.new_hand()
            return
        
        # Continue with normal betting round logic for 2+ active non-all-in players
        if len(action_players) > 1:
            all_bets_equal = len({p['bet'] for p in action_players}) == 1
            all_have_acted = all(p['acted'] for p in action_players)
            if all_bets_equal and all_have_acted:
                self.new_street()
                return
        
        # Find next player to act (existing logic but simplified)
        next_player = (self.current_player + 1) % len(self.players)
        attempts = 0
        while attempts < len(self.players):
            if self.players[next_player]['status'] == 'active' and not self.players[next_player]['allin']:
                break
            next_player = (next_player + 1) % len(self.players)
            attempts += 1
        
        if attempts >= len(self.players):
            # This shouldn't happen now with the above logic, but keeping as safety
            print("ERROR: No valid next player found, advancing to showdown")
            while self.street < 4:
                self.new_street()
            return
        
        #otherwise, just move on to next player in round of betting, dump gamestate
        self.current_player = next_player
        with open("game_state.json", "w") as f:
            json.dump(self.get_game_state(), f, indent=4)
        # if Decimal(str((self.starting_players * self.starting_stack))) != sum(all_bb):
        #     raise Exception(f'Invalid gamestate occurred: {Decimal(str((self.starting_players * self.starting_stack)))} != {sum(all_bb)}')


    def new_street(self):
        if self.street == 0:
            self.street = 1
            self.end_betting_round()
            self.deal_flop()
            return
        elif self.street == 1:
            self.street = 2
            self.end_betting_round()
            self.deal_turn()
            return
        elif self.street == 2:
            self.street = 3
            self.end_betting_round()
            self.deal_river()
            return
        elif self.street == 3:
            self.street = 4
            self.end_betting_round()
            self.showdown()
        else:
            print("Error: Trying to advance past showdown!")
            return

            
    def end_betting_round(self):
        """End of Betting Round Logic"""
        allin_players = [player for player in self.players if player['allin'] == True]
        allin_players_contribs = sorted([player['contrib'] for player in allin_players]) # smallest to largest contribs of allin players
        
        #visualize
        pot_contributions = [player['contrib'] for player in self.players]      #index of pot_contributions is player seat number
        #print(pot_contributions)

        #no players are all in
        if allin_players == []:
            # Clear betting round related player states, put bets in main pot
            for player in self.players:
                player['acted'] = False
                player['bet'] = Decimal("0.00")
            self.main_pot = self.q(self.pot)  # put bets in main pot (unchanged behavior)

        else:
            # There are all-in players -> build main pot + side pots from contributions
            #pots = self.build_pots()   # list of {'amount', 'eligible'}
            # map amounts to display fields for debugging/JSON/visualization
            #self.clear_pots_fields(pots)

            # Clear per-round state (bets become zero; contrib keeps the full contributed amount)
            for player in self.players:
                player['acted'] = False
                player['bet'] = Decimal("0.00")

            # Note: we don't automatically payout here. Payout should happen at showdown,
            # using self.payout_pots(pots, winners_by_rank) once you have hand evaluation results.

        #showdown is last betting round
        if self.street == 4:
            return
        #start with small blind position for next betting round, if 2+ active non allin players remain
        # (note: original code had a bug checking 'active' key — keep semantic but correct to 'status')
        active_non_allin = [player for player in self.players if player['status'] == 'active' and player['allin'] == False]
        if len(active_non_allin) > 1:
            next_player = (self.dealer_position + 1 ) % len(self.players)
            while self.players[next_player]['status'] != 'active' or self.players[next_player]['allin'] == True:
                next_player = (next_player + 1) % len(self.players)
            self.current_player = next_player
            print(f'Next betting round starts with player {self.current_player}')

    def process_action(self, action):
        """
        Process a player action
            action: str: 'quit', 'check/fold', 'call/minbet', 'bet1/2pot', 'bet3/4pot', 'betpot'
        """
        if action == 'check/fold':
            self.handle_checkfold()
            self.players[self.current_player]['acted'] = True
        elif action == 'call/minbet':
            self.handle_callminbet()
            self.players[self.current_player]['acted'] = True
        elif action == 'bet1/2pot':
            self.handle_bethalfpot()
            self.players[self.current_player]['acted'] = True
        elif action == 'bet3/4pot':
            self.handle_betthreequarterspot()
            self.players[self.current_player]['acted'] = True
        elif action == 'betpot':
            self.handle_betpot()
            self.players[self.current_player]['acted'] = True
    
    def deal_flop(self):
        """Deal the flop (3 community cards)"""
        self.community_cards.append(self.deal_card())
        self.community_cards.append(self.deal_card())
        self.community_cards.append(self.deal_card())
        print("Dealing flop...")
    
    def deal_turn(self):
        """Deal the turn (4th community card)"""
        self.community_cards.append(self.deal_card())
        print("Dealing turn...")
    
    def deal_river(self):
        """Deal the river (5th community card)"""
        self.community_cards.append(self.deal_card())
        print("Dealing river...")
    
    def showdown(self):
        """Evaluate hands and determine winners"""
        for p in self.players:
            p['stack'] = Decimal('10.00')
            p['acted'] = False
        return
        # Build pots from contributions (main + side pots)
        pots = self.build_pots()
        self.clear_pots_fields(pots)  # update the side_pot fields for display/debug

        # If only one active player, pay them everything (existing behavior)
        active_players = [p for p in self.players if p['status'] == 'active']

        # Otherwise: you must evaluate hands and produce winners_by_rank:
        # winners_by_rank = [ [player1], [player2, player3], ... ]
        # Then call:
        #   self.payout_pots(pots, winners_by_rank)
        #
        # (Hand evaluation not implemented here — insert your evaluator and then call payout_pots.)
        # Reset pot, street, update dealer position, deal new cards, reset player flags, community cards
        self.pot, self.main_pot, self.side_pot = Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
        self.side_pot1, self.side_pot2, self.side_pot3 = Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
        self.side_pot4, self.side_pot5, self.side_pot6, self.side_pot7 = Decimal("0.00"), Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
        self.street = 0
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        self.community_cards = []
        self.init_deck()
        for player in self.players:
            player['bet'] = Decimal("0.00")
            player['status'] = 'active'
            player['cards'] = [self.deal_card(), self.deal_card(), self.deal_card(), self.deal_card()]
            player['acted'] = False
            player['allin'] = False
            player['contrib'] = Decimal("0.00")   # reset contribution for new hand

        print("SHOWDOWN (pots built; awaiting hand evaluation to payout)")
        
        # leave new_hand() to be called after payout happens externally once you evaluate hands.

    def handle_checkfold(self):
        """Handle 0 bet (check or fold depending on gamestate)"""
        #find max bet
        min_to_play = max(player['bet'] for player in self.players)

        #determine if 0 bet is a check or fold
        if self.players[self.current_player]['bet'] == min_to_play:
            print(f"Player {self.current_player} checks")
        else:
            self.players[self.current_player]['status'] = 'folded'
            #self.players[self.current_player]['cards'] = []
            print(f"Player {self.current_player} folds")
    
    def handle_callminbet(self):
        """Handle minimum bet (call or min bet depending on gamestate)"""
        #find max bet
        min_to_play = max(player['bet'] for player in self.players)
        current_bet = self.players[self.current_player]['bet']

        #min bet is 1bb
        if min_to_play == Decimal("0.00"):
            #not all in
            if self.players[self.current_player]['stack'] > Decimal("1.00"):
                self.players[self.current_player]['bet'] = Decimal("1.00")
                added = Decimal("1.00") - current_bet
                self.players[self.current_player]['stack'] -= added
                self.players[self.current_player]['contrib'] += added
                self.pot += added
                for player in self.players:
                    player['acted'] = False
                print(f"Player {self.current_player} bets 1bb")
            #all in
            else:
                added = self.players[self.current_player]['stack']
                self.players[self.current_player]['bet'] += added
                self.players[self.current_player]['contrib'] += added
                self.players[self.current_player]['stack'] = Decimal("0.00")
                self.pot += added
                self.players[self.current_player]['allin'] = True
                for player in self.players:
                    player['acted'] = False
                print(f"Player {self.current_player} goes all in with {self.players[self.current_player]['bet']}bb")
        #min bet is a call
        else:
            to_call = self.q(min_to_play - current_bet)
            #not all in
            if self.players[self.current_player]['stack'] > to_call:
                self.players[self.current_player]['bet'] = self.q(min_to_play)
                self.players[self.current_player]['stack'] -= to_call
                self.players[self.current_player]['contrib'] += to_call
                self.pot += to_call
                print(f"Player {self.current_player} calls {min_to_play}bb")
            #all in
            else:
                added = self.players[self.current_player]['stack']
                self.players[self.current_player]['bet'] += added
                self.players[self.current_player]['contrib'] += added
                self.pot += added
                self.players[self.current_player]['stack'] = Decimal("0.00")
                self.players[self.current_player]['allin'] = True
                print(f"Player {self.current_player} goes all in with {self.players[self.current_player]['bet']}bb")
    
    def handle_bethalfpot(self):
        """Handle 1/2 pot bet"""
        #find max bet // amount to call
        min_to_play = max(player['bet'] for player in self.players)
        current_bet = self.players[self.current_player]['bet']
        pot = (self.pot - current_bet) + (Decimal("2.00") * min_to_play)
        pot12 = (Decimal("0.5") * pot).quantize(CENTS)
        if pot12 < Decimal("2.00"): pot12 = Decimal("2.00")     #min allowed bet preflop that's not a call

        #not all in
        amount_needed = self.q(pot12 - current_bet)
        if self.players[self.current_player]['stack'] > amount_needed:
            self.players[self.current_player]['bet'] = self.q(pot12)
            self.players[self.current_player]['stack'] -= amount_needed
            self.players[self.current_player]['contrib'] += amount_needed
            self.pot += amount_needed
            for player in self.players:
                    player['acted'] = False
            print(f"Player {self.current_player} bets 1/2 pot: {pot12}bb")
        #all in
        else:
            added = self.players[self.current_player]['stack']
            self.players[self.current_player]['bet'] += added
            self.players[self.current_player]['contrib'] += added
            self.pot += added
            self.players[self.current_player]['stack'] = Decimal("0.00")
            self.players[self.current_player]['allin'] = True
            if self.players[self.current_player]['bet'] > min_to_play:
                for player in self.players:
                        player['acted'] = False
            print(f"Player {self.current_player} goes all in with {self.players[self.current_player]['bet']}bb")
        
    
    def handle_betthreequarterspot(self):
        """Handle 3/4 pot bet"""
        #find max bet // amount to call
        min_to_play = max(player['bet'] for player in self.players)
        current_bet = self.players[self.current_player]['bet']
        pot = (self.pot - current_bet) + (Decimal("2.00") * min_to_play)
        pot34 = (Decimal("0.75") * pot).quantize(CENTS)
        if pot34 < Decimal("2.00"): pot34 = Decimal("2.00")     #min allowed bet preflop that's not a call
        
        amount_needed = self.q(pot34 - current_bet)
        #not all in
        if self.players[self.current_player]['stack'] > amount_needed:
            self.players[self.current_player]['bet'] = self.q(pot34)
            self.players[self.current_player]['stack'] -= amount_needed
            self.players[self.current_player]['contrib'] += amount_needed
            self.pot += amount_needed
            for player in self.players:
                    player['acted'] = False
            print(f"Player {self.current_player} bets 3/4 pot: {pot34}bb")
        #all in
        else:
            added = self.players[self.current_player]['stack']
            self.players[self.current_player]['bet'] += added
            self.players[self.current_player]['contrib'] += added
            self.pot += added
            self.players[self.current_player]['stack'] = Decimal("0.00")
            self.players[self.current_player]['allin'] = True
            if self.players[self.current_player]['bet'] > min_to_play:
                for player in self.players:
                        player['acted'] = False
            print(f"Player {self.current_player} goes all in with {self.players[self.current_player]['bet']}bb")
    
    def handle_betpot(self):
        """Handle pot bet"""
        #find max bet // amount to call
        min_to_play = max(player['bet'] for player in self.players)
        current_bet = self.players[self.current_player]['bet']
        pot = (self.pot - current_bet) + (Decimal("2.00") * min_to_play)
        pot = pot.quantize(CENTS)

        amount_needed = self.q(pot - current_bet)
        #not all in
        if self.players[self.current_player]['stack'] > amount_needed:
            self.players[self.current_player]['bet'] = self.q(pot)
            self.players[self.current_player]['stack'] -= amount_needed
            self.players[self.current_player]['contrib'] += amount_needed
            self.pot += amount_needed
            for player in self.players:
                    player['acted'] = False
            print(f"Player {self.current_player} bets pot: {pot}bb")
        #all in
        else:
            added = self.players[self.current_player]['stack']
            self.players[self.current_player]['bet'] += added
            self.players[self.current_player]['contrib'] += added
            self.pot += added
            self.players[self.current_player]['stack'] = Decimal("0.00")
            self.players[self.current_player]['allin'] = True
            if self.players[self.current_player]['bet'] > min_to_play:
                for player in self.players:
                        player['acted'] = False
            print(f"Player {self.current_player} goes all in with {self.players[self.current_player]['bet']}bb")

    def init_deck(self):
        self.deck = [
            'C2', 'D2', 'S2', 'H2',
            'C3', 'D3', 'S3', 'H3',
            'C4', 'D4', 'S4', 'H4',
            'C5', 'D5', 'S5', 'H5',
            'C6', 'D6', 'S6', 'H6',
            'C7', 'D7', 'S7', 'H7',
            'C8', 'D8', 'S8', 'H8',
            'C9', 'D9', 'S9', 'H9',
            'C10','D10','S10','H10',
            'CJ', 'DJ', 'SJ', 'HJ',
            'CQ', 'DQ', 'SQ', 'HQ',
            'CK', 'DK', 'SK', 'HK',
            'CA', 'DA', 'SA', 'HA'
        ]
        random.shuffle(self.deck)
        random.shuffle(self.deck)   # shuffle twice for good measure
        self.deck.reverse()

    def deal_card(self):
        return self.deck.pop()
