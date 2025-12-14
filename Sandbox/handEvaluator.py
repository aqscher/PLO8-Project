from itertools import combinations
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.utils.card_utils import gen_cards

def evalHi(game_state):
    """
    Returns:
        winners  -> list of player indexes who tied for best hand
        winhands -> list of their 5-card winning hands (string form)
    """

    board = gen_cards(game_state['community_cards'])

    # Convert each player’s cards into evaluator format
    all_players = [gen_cards(p['cards']) for p in game_state['players']]

    best_rank = -10**18
    best_hands = []       # store tuples: (player_idx, rank, hand_cards)

    # Evaluate each player
    for p_idx, hole_cards in enumerate(all_players):

        player_best_rank = -10**18
        player_best_hand = None

        # All 6 combos of 2 hole cards
        for hole_combo in combinations(hole_cards, 2):
            # All 10 combos of 3 board cards
            for board_combo in combinations(board, 3):
                rank = HandEvaluator.eval_hand(list(hole_combo), list(board_combo))

                if rank > player_best_rank:
                    player_best_rank = rank
                    player_best_hand = list(hole_combo) + list(board_combo)

        # Track this player’s best
        best_hands.append((p_idx, player_best_rank, player_best_hand))

        # Track table best
        if player_best_rank > best_rank:
            best_rank = player_best_rank

    # Determine winners
    winners = []
    winning_hands = []

    for p_idx, rank, hand in best_hands:
        if rank == best_rank:
            winners.append(game_state['players'][p_idx])  # <- store dict, not index
            winning_hands.append([str(c) for c in hand])

    return winners, winning_hands


from itertools import combinations

def evalLo(game_state):
    """
    Evaluate 8-or-better low hands for each player (Aces count as 1).
    Returns winners as player dicts and the winning hands.
    """
    board = gen_cards(game_state['community_cards'])
    all_players = [gen_cards(p['cards']) for p in game_state['players']]

    best_low_val = None
    best_hands = []

    for p_idx, hole_cards in enumerate(all_players):
        player_best_low = None
        player_best_hand = None

        # All 2-card hole combos
        for hole_combo in combinations(hole_cards, 2):
            # All 3-card board combos
            for board_combo in combinations(board, 3):
                hand = list(hole_combo) + list(board_combo)

                # Convert Ace -> 1
                low_ranks = [1 if c.rank == 14 else c.rank for c in hand]

                # Valid low: all ≤8
                if max(low_ranks) > 8:
                    continue

                # Distinct ranks
                if len(set(low_ranks)) < 5:
                    continue

                # Sort descending: highest card first
                low_val = tuple(sorted(low_ranks, reverse=True))

                if player_best_low is None or low_val < player_best_low:
                    player_best_low = low_val
                    player_best_hand = hand

        if player_best_low is None:
            continue

        if best_low_val is None or player_best_low < best_low_val:
            best_low_val = player_best_low
            best_hands = [(p_idx, player_best_hand)]
        elif player_best_low == best_low_val:
            best_hands.append((p_idx, player_best_hand))

    winners = [game_state['players'][p_idx] for p_idx, _ in best_hands]
    winning_hands = [[str(c) for c in hand] for _, hand in best_hands]

    return winners, winning_hands


