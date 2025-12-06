"""
PLO8 Poker Engine - Hand Evaluator
Evaluates both high and low hands for Pot Limit Omaha Hi-Lo (8-or-better)

PLO8 Rules:
- Must use EXACTLY 2 cards from hole cards and 3 from board
- Low hand qualifies only if 5 cards are 8 or lower (with Ace counting as 1)
- Straights and flushes don't count against low hands
- Aces are low (A-2-3-4-5 is best low)
"""

from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.utils.card_utils import gen_cards

cards = gen_cards(["HA", "HK"])
board = gen_cards(["C4", "H2", "HQ", "HJ", "HT"])

rank = HandEvaluator.eval_hand(cards, board)
print(rank)

cards = gen_cards(["H2", "H3"])
board = gen_cards(["C4", "H5", "H7", "C8", "C9"])

rank = HandEvaluator.eval_hand(cards, board)
print(rank)

cards = gen_cards(["CA", "CK"])
board = gen_cards(["C4", "H2", "CQ", "CJ", "CT"])

rank = HandEvaluator.eval_hand(cards, board)
print(rank)
