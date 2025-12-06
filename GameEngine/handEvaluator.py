from itertools import combinations
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.utils.card_utils import gen_cards

def evalHi(game_state):
    best_rank = -10**18
    best_hand = None
    # player_hands_str = [player['cards'] for player in game_state['players']]
    # board5 = gen_cards(game_state['community_cards'])
    player_hands_str = [ [ 'HK', 'HA', 'H3', 'H4' ], [ 'C2', 'C4', 'D5', 'D8' ] ] # comment this and below line out and uncomment^
    board5 = gen_cards(['CT', 'SJ', 'SQ', 'C8', 'H2'])
    player_hands = []
    for i in player_hands_str:
        player_hands.append(gen_cards(i))
    for i in player_hands:
    # 2 hole cards (C(4,2) = 6)
        for hole_combo in combinations(i, 2):

            # 3 board cards (C(5,3) = 10)
            for board_combo in combinations(board5, 3):
                rank = HandEvaluator.eval_hand(list(hole_combo), list(board_combo))

                if rank > best_rank:
                    best_rank = rank
                    best_hand = list(hole_combo) + list(board_combo)
    best_hand = [str(c) for c in best_hand]
    return best_rank, best_hand

def evalLo(game_state):
    pass

print(evalHi([]))