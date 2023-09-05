import typing as t
from enum import Enum


class PokerBaseError(Exception):
    pass


class OutOfChipsError(PokerBaseError):
    pass


class TooManyCardsError(PokerBaseError):
    pass


class Suit(str, Enum):
    club = "club"
    spade = "spade"
    diamond = "diamond"
    heard = "heart"


class Value(int, Enum):
    ace = "1"
    two = "2"
    three = "3"
    four = "4"
    five = "5"
    six = "6"
    seven = "7"
    eight = "8"
    nine = "9"
    ten = "10"
    jack = "11"
    queen = "12"
    king = "13"


class Card:
    def __init__(self, suit: Suit, value_):
        self._suit = suit
        self.value = value_


class Hand:
    def __init__(self, cards: t.List[Card]):
        self._cards = cards

    def __gt__(self, other):
        pass

    def __lt__(self, other):
        pass

    def __eq__(self, other):
        if not isinstance(other, Hand):
            raise TypeError

    def __len__(self):
        return len(self._cards)

    def add_cards(self, cards: t.List[Card]):
        if len(self._cards) == 5:
            raise ValueError("Hand already has 5 cards")
        self._cards.extend(cards)

    def _check_for_straight(self):
        self._cards.sort(key=lambda x: x.value)  # TODO this will break for the ace. It is both 1 and 14
        prev_card = self._cards[0]
        for card in self._cards[1:]:
            if prev_card.value + 1 != card.value:
                return False

    def _check_flush(self):
        pass


class Player:
    def __init__(self, name: str, chips: int):
        self._name = name
        self._chips = chips
        self._hand = Hand([])
        self._win_count = 0
        self._lose_count = 0

    def _new_hand(self):
        self._hand = Hand([])

    def bet(self, bet_amount: int):
        if bet_amount > self._chips:
            raise OutOfChipsError
        self._chips -= bet_amount

    def win(self, win_amount: int):
        self._chips += win_amount
        self._win_count += 1
        self._new_hand()

    def lose(self):
        self._lose_count += 1
        self._new_hand()

    def new_cards(self, cards: t.List[Card]):
        if len(self._hand) + len(cards) > 5:
            raise TooManyCardsError
        self._hand.add_cards(cards)
