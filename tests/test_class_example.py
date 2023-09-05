from texas_holdem.class_example import Card, Player, OutOfChipsError, TooManyCardsError, Hand, Suit, Value
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
    player.new_cards([Card(Suit.club, Value.two), Card(Suit.club, Value.three)])
    player.new_cards([Card(Suit.club, Value.four), Card(Suit.club, Value.five), Card(Suit.club, Value.six)])
    with pytest.raises(TooManyCardsError):
        player.new_cards([Card(Suit.club, Value.seven)])


HANDS = [
    {
        # Straight flush
        "winning": Hand(
            [
                Card(Suit.club, Value.two),
                Card(Suit.club, Value.three),
                Card(Suit.club, Value.four),
                Card(Suit.club, Value.five),
                Card(Suit.club, Value.six),
            ]
        ),
        # Flush
        "loosing": Hand(
            [
                Card(Suit.club, Value.two),
                Card(Suit.club, Value.three),
                Card(Suit.club, Value.four),
                Card(Suit.club, Value.five),
                Card(Suit.club, Value.seven),
            ]
        ),
    },
    {
        # pair
        "winning": Hand(
            [
                Card(Suit.club, Value.two),
                Card(Suit.diamond, Value.two),
                Card(Suit.club, Value.four),
                Card(Suit.club, Value.five),
                Card(Suit.club, Value.six),
            ]
        ),
        # high card
        "loosing": Hand(
            [
                Card(Suit.club, Value.two),
                Card(Suit.club, Value.three),
                Card(Suit.club, Value.four),
                Card(Suit.club, Value.five),
                Card(Suit.diamond, Value.seven),
            ]
        ),
    },
]


@pytest.mark.parametrize("hand", HANDS)
def test_hand(hand):
    winning = hand["winning"]
    loosing = hand["loosing"]
    assert winning > loosing
