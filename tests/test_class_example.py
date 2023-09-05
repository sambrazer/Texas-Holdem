from texas_holdem.class_example import Card, Player, OutOfChipsError, TooManyCardsError, Hand
import pytest


def test_player_money():
    player = Player("Test", 100)
    assert player._chips == 100


def test_player_bet():
    player = Player("Test", 100)
    player.bet(50)
    assert player._chips == 50


def test_player_bet_excessive():
    player = Player("Test", 100)
    with pytest.raises(OutOfChipsError):
        player.bet(150)


def test_player_win():
    player = Player("Test", 100)
    player.bet(50)
    player.win(100)
    assert player._chips == 150
    assert player._win_count == 1
    assert player._lose_count == 0


def test_player_cards():
    player = Player("Test", 100)
    player.new_cards([Card(2, "H"), Card(3, "H")])
    player.new_cards([Card(4, "H"), Card(5, "H"), Card(6, "H")])
    with pytest.raises(TooManyCardsError):
        player.new_cards([Card(7, "H")])


HANDS = [
    {
        # Straight flush
        "winning": Hand([Card(2, "H"), Card(3, "H"), Card(4, "H"), Card(5, "H"), Card(6, "H")]),
        # Flush
        "loosing": Hand([Card(2, "H"), Card(3, "H"), Card(4, "H"), Card(5, "H"), Card(6, "D")]),
    },
    {
        # pair
        "winning": Hand([Card(2, "H"), Card(2, "D"), Card(4, "H"), Card(5, "H"), Card(6, "H")]),
        # high card
        "loosing": Hand([Card(2, "H"), Card(3, "D"), Card(4, "H"), Card(5, "H"), Card(7, "H")]),
    }
]


@pytest.mark.parametrize("hand", HANDS)
def test_hand(hand):
    winning = hand["winning"]
    loosing = hand["loosing"]
    assert winning > loosing
