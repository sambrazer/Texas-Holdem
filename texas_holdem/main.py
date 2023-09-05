from enum import Enum

import numpy as np
import pandas as pd
import datetime
from datetime import date
import random
import os
import pathlib

class game_param:
    initial_money = 100000
    big_blind = 10000
    little_blind = 5000

    names = pd.read_csv(pathlib.Path("./names.csv"))['name'].to_list()

    def get_players():
        num_players = input('How many bots (max 9): ')
        if num_players.isdigit() == False:
            print('Invalid choice. Try again.')
            return(False)
        elif int(num_players) > 9 or int(num_players) <= 0:
            print('Invalid choice. Try again.')
            return(False)
        return(int(num_players))

    def player_names(num_players):
        players = []
        for i in range(num_players - 1):
            bool = True
            player = random.choice(game_param.names)
            while bool == True:
                if player in players:
                    player = random.choice(game_param.names)
                else:
                    players.append(player)
                    bool = False
        user_name = input('What is your First and Last name: ')
        players.append(user_name)
        return(players)


    def designate_players(players, turn, participate_dict, previous_players, previous_dealer, original_players):
        '''if the dropped player is before the dealer or the previous dealer, offset by 1. if it is after the dealer no offset'''
        if len(players) == len(original_players):
            dealer = players[turn % len(players)]
            lb = players[(turn + 1) % len(players)]
            bb = players[(turn + 2) % len(players)]
        elif len(players) >= 3:
            if previous_dealer in players:
                dealer = players[players.index(previous_dealer) + 1]
            elif previous_dealer not in players:
                for i in range(1, len(previous_players) + 1):
                    if previous_players[previous_players.index(previous_dealer) + i] in players:
                        dealer = previous_players[previous_players.index(previous_dealer) + i]
                        break
            lb = players[players.index(dealer) + 1]
            bb = players[players.index(dealer) + 2]
        else:
            if previous_dealer in players:
                dealer = players[players.index(previous_dealer) + 1]
            else:
                for i in range(1, len(previous_players) + 1):
                    if previous_players[previous_players.index(previous_dealer) + i] in players:
                        dealer = previous_players[previous_players.index(previous_dealer) + i]
                        break
            lb = ''
            bb = players[players.index(dealer) + 2]
        previous_dealer = dealer
        previous_players = players
        return((dealer, bb, lb, previous_dealer, previous_players))

    def player_wallets_initial(players, initial_money):
        wallet_dict = {}
        for player in players:
            wallet_dict[player] = initial_money
        return(wallet_dict)



class game_mech:

    def game_start():
        print('*****GAME START*****\n')
        bool = False
        while bool == False:
            bots = game_param.get_players()
            if type(bots) != int:
                del bots
            else: bool = True
        return(bots)

    def initialize_deck():
        deck = []
        for suit in ['S', 'C', 'D', 'H']:
            for key, value in hands.cards_dict.items():
                deck.append(key + suit)
        return(deck)

    def shuffle_deck():
        deck = game_mech.initialize_deck()
        num_shuffles = random.randint(3, 7)
        for shuffle in range(num_shuffles):
            random.shuffle(deck)
        deck = deck[26:] + deck[:26]
        return(deck)

    def deal_cards_players(players, shuffled_deck, participate_dict):
        player_dict = {}
        for player in players:
            if participate_dict.get(player) == False: continue
            player_dict[player] = [shuffled_deck[players.index(player)], shuffled_deck[players.index(player) + len(players)]]
        return((player_dict, shuffled_deck[len(players)*2: ]))

    def deal_flop(shuffled_deck):
        table_cards_dict = {}
        table_cards_dict['Burn'] = shuffled_deck[:6:2]
        table_cards_dict['Flop'] = shuffled_deck[1:6:2]
        return((table_cards_dict, shuffled_deck[6:]))

    def deal_turn(table_cards_dict, shuffled_deck):
        table_cards_dict['Burn'] = table_cards_dict['Burn'] + [shuffled_deck[0]]
        table_cards_dict['Turn'] = [shuffled_deck[1]]
        return((table_cards_dict, shuffled_deck[2:]))

    def deal_river(table_cards_dict, shuffled_deck):
        table_cards_dict['Burn'] = table_cards_dict['Burn'] + [shuffled_deck[0]]
        table_cards_dict['River'] = [shuffled_deck[1]]
        return((table_cards_dict, shuffled_deck[2:]))

    def wallet_update(player, wallet_dict, bet):
        wallet_dict[player] = wallet_dict.get(player) - bet
        return(wallet_dict)

    def define_turn_order(players, dealer, lb, bb):
        if players.index(bb) == len(players) - 1:
            players_ordered = players
        else:
            players_ordered = players[(players.index(bb)+1) % len(players):] + players[:players.index(bb) + 1]
        return(players_ordered)

    def blind_bet(players, wallet_dict, lb, bb):
        '''Need else codes for big and little blinds to put them all in if they cant match the blind'''
        bet_dict = {}
        for player in players:
            if player == bb:
                if wallet_dict.get(player) >= game_param.big_blind:
                    bet_dict[player] = game_param.big_blind
                    wallet_dict[player] = wallet_dict.get(player) - game_param.big_blind
            elif player == lb:
                if wallet_dict.get(player) >= game_param.little_blind:
                    bet_dict[player] = game_param.little_blind
                    wallet_dict[player] = wallet_dict.get(player) - game_param.little_blind
            else:
                bet_dict[player] = 0
        blind_pot_value = sum(list(bet_dict.values()))
        return((wallet_dict, bet_dict, blind_pot_value))

    def get_bet_user(player, wallet_dict, bet_dict, participate_dict):
        if participate_dict.get(player) == False:
            move = 'fold'
            return((wallet_dict, bet_dict, participate_dict, move))
        elif participate_dict.get(player) == True and wallet_dict[player] == 0:
            move = 'side pot'
            return((wallet_dict, bet_dict, participate_dict, move))
        else:
            bool_choice = False
            bool_bet = False
            possible_choices = ['bet', 'knock', 'fold', 'call']
            while bool_choice == False:
                choice = input('Bet, knock, call, or fold: ')
                if choice.lower() not in possible_choices or (choice.lower() == 'knock' and bet_dict.get(player) != max(list(bet_dict.values()))):
                    print('Invalid choice. Choose again.')
                elif choice.lower() == 'call' and (wallet_dict.get(player) >= max(list(bet_dict.values())) and max(list(bet_dict.values())) > 0):
                    move = 'call'
                    wallet_dict[player] = wallet_dict.get(player) - max(list(bet_dict.values()))
                    bet_dict[player] = max(list(bet_dict.values()))
                    bool_choice = True
                    return((wallet_dict, bet_dict, participate_dict, move))
                elif choice.lower() == 'call' and (wallet_dict.get(player) < max(list(bet_dict.values())) or max(list(bet_dict.values())) == 0):
                    print('Invalid choice. Choose again.')
                elif choice.lower() == 'bet':
                    while bool_bet == False:
                        bet = input('Enter bet amount: ')
                        if bet.isdigit() == False or (float(bet) < max(list(bet_dict.values())) and float(bet) < wallet_dict.get(player)) or float(bet) > wallet_dict.get(player):
                            print('Invalid choice. Choose again.')
                        else:
                            if int(bet) == wallet_dict[player] or max(list(bet_dict.values())) > wallet_dict.get(player):
                                move = 'all in'
                                bool_bet = True
                            else:
                                move = 'bet'
                                bool_bet = True
                            bet_dict[player] = bet_dict.get(player) + int(bet)
                            wallet_dict = game_mech.wallet_update(player, wallet_dict, int(bet))
                    bool_choice = True

                elif choice.lower() == 'fold':
                    move = 'fold'
                    participate_dict[player] = False
                    bool_choice = True

                else:
                    move = 'knock'
                    bool_choice = True

            '''else:
                print('Choice:', choice)
                print('Bet:', bet_dict.get(player))
                print('Wallet:', wallet_dict.get(player))    '''

            return((wallet_dict, bet_dict, participate_dict, move))

    def get_bet_bots(player, wallet_dict, bet_dict, participate_dict):
        if max(list(bet_dict.values())) == 0:
            move = 'knock'
            return((wallet_dict, bet_dict, participate_dict, move))
        elif participate_dict.get(player) == False:
            move = 'fold'
            return((wallet_dict, bet_dict, participate_dict, move))
        elif wallet_dict.get(player) + bet_dict.get(player) < max(bet_dict.values()):
            move = 'all in'
            bet_dict[player] = wallet_dict.get(player) + bet_dict.get(player)
            wallet_dict[player] = 0
            return((wallet_dict, bet_dict, participate_dict, move))
        elif wallet_dict.get(player) == 0 and participate_dict.get(player) == True:
            move = 'all in'
            return((wallet_dict, bet_dict, participate_dict, move))
        else:
            increment_bet = max(list(bet_dict.values())) - bet_dict.get(player)
            if increment_bet > wallet_dict.get(player):
                bet_dict[player] = bet_dict.get(player) + wallet_dict.get(player)
                wallet_dict[player] = 0
            else:
                bet_dict[player] = max(list(bet_dict.values()))
                wallet_dict[player] = wallet_dict.get(player) - increment_bet
        move = 'call'
        return((wallet_dict, bet_dict, participate_dict, move))

    def bet_loop(players, wallet_dict, bet_dict, participate_dict, players_ordered, pot_value, side_pots, side_pot_participants_list):
        bet_bool = False
        move_dict = {}
        last_to_bet = ''
        while bet_bool == False:
            for player in players_ordered:
                if player == last_to_bet or list(participate_dict.values()).count(True) == list(move_dict.values()).count('call') or list(participate_dict.values()).count(True)== list(move_dict.values()).count('knock'):
                    bet_bool = True
                    break
                if player == players[-1]:
                    wallet_dict, bet_dict, participate_dict, move = game_mech.get_bet_user(player, wallet_dict, bet_dict, participate_dict)
                    move_dict[player] = move
                else:
                    wallet_dict, bet_dict, participate_dict, move = game_mech.get_bet_bots(player, wallet_dict, bet_dict, participate_dict)
                    move_dict[player] = move
                if move_dict[player] == 'bet' or (move_dict[player] == 'all in' and max(list(bet_dict.values())) == bet_dict[player]):
                    last_to_bet = player
        if 'all in' in list(move_dict.values()) and list(participate_dict.values()).count(True) > 1:
            pot_value, side_pots, side_pot_participants_list = game_mech.side_pot(players, participate_dict, wallet_dict, bet_dict, pot_value, side_pots)
        else:
            pot_value = pot_value + sum(list(bet_dict.values()))
        return((wallet_dict, bet_dict, participate_dict, pot_value, side_pots, side_pot_participants_list))

    def determine_winner(rank, best_hands, players, participate_dict, table_cards_dict):
        best_playing_rank = max([value for idx, value in enumerate(rank) if participate_dict.get(players[idx]) == True])
        initial_best_rank_index = [idx for idx, value in enumerate(rank) if value == best_playing_rank and participate_dict.get(players[idx]) == True]
        best_rank_index = [value for idx, value in enumerate(initial_best_rank_index) if participate_dict.get(players[value]) == True]
        hands_to_compare = [best_hands[i] for i in best_rank_index if list(participate_dict.values())[i] == True]
        winning_hands = []
        winning_players = []
        if len(best_rank_index) > 1:
            if max(rank) not in [2, 3, 4, 7, 8]:
                evaluate_duplicates_number = []
                for hand in hands_to_compare:
                    print(hand)
                    for card in hand:
                        print(card[:-1])
                        evaluate_duplicates_number.append(hands.cards_dict.get(card[:-1]))
                try:
                    high_card_number = [key for key, value in hands.cards_dict.items() if value == max(evaluate_duplicates_number)][0]
                except:
                    print('High Card interpretation ranking busted')
                    print(evaluate_duplicates_number)
                    _ = input('')
                for hand in hands_to_compare:
                    if participate_dict.get(player[best_hands.index(hand)]) == False: continue
                    for card in hand:
                        if high_card_number == card[:-1]:
                            winning_hands.append(hand)
                            winning_players.append(players[best_hands.index(hand)])
                            break
            elif max(rank) == 2:
                high_pair = []
                high_single = []
                med_single = []
                low_single = []
                for hand in hands_to_compare:
                    high_pair.append(hands.cards_dict.get(hand[0][:-1]))
                    high_single.append(hands.cards_dict.get(hand[2][:-1]))
                    med_single.append(hands.cards_dict.get(hand[3][:-1]))
                    low_single.append(hands.cards_dict.get(hand[4][:-1]))
                if len(high_pair) == len(set(high_pair)):
                    winning_hands = [hands_to_compare[high_pair.index(max(high_pair))]]
                    winning_players = [players[best_rank_index[high_pair.index(max(high_pair))]]]
                else:
                    high_single_index = [idx for idx, value in enumerate(high_pair) if value == max(high_pair)]
                    high_single_tied = [high_single[i] for i in high_single_index]
                    if len(high_single_tied) == len(set(high_single_tied)):
                        winning_hands = [hands_to_compare[high_single_index[high_single_tied.index(max(high_single_tied))]]]
                        winning_players = [players[best_rank_index[high_single_index[high_single_tied.index(max(high_single_tied))]]]]
                    else:
                        med_single_index = [idx for idx, value in enumerate(high_single) if value == max(high_single_tied) and idx in high_single_index]
                        med_single_tied = [med_single[i] for i in med_single_index]
                        if len(med_single_tied) == len(set(med_single_tied)):
                            winning_hands = [hands_to_compare[med_single_index[med_single_tied.index(max(med_single_tied))]]]
                            winning_players = [players[best_rank_index[med_single_index[med_single_tied.index(max(med_single_tied))]]]]
                        else:
                            low_single_index = [idx for idx, value in enumerate(med_single) if value == max(med_single_tied) and idx in med_single_index]
                            low_single_tied = [low_single[i] for i in low_single_index]
                            if len(low_single_tied) == len(set(low_single_tied)):
                                winning_hands = [hands_to_compare[low_single_index[low_single_tied.index(max(low_single_tied))]]  ]
                                winning_players = [players[best_rank_index[low_single_index[low_single_tied.index(max(low_single_tied))]]]]
                            else:
                                winning_index = [idx for idx, value in enumerate(low_single) if value == max(low_single_tied) and idx in low_single_index]
                                winning_hands = [hands_to_compare[i] for i in winning_index]
                                winning_players = [players[best_rank_index[i]] for i in winning_index]
            elif max(rank) == 3:
                high_pair = []
                low_pair = []
                high_single = []
                for hand in hands_to_compare:
                    high_pair.append(hands.cards_dict.get(hand[0][:-1]))
                    low_pair.append(hands.cards_dict.get(hand[2][:-1]))
                    high_single.append(hands.cards_dict.get(hand[4][:-1]))
                    if len(high_pair) == len(set(high_pair)):
                        winning_hands = [hands_to_compare[high_pair.index(max(high_pair))]]
                        winning_players = [players[best_rank_index[high_pair.index(max(high_pair))]]]
                    else:
                        low_pair_tied_index = [idx for idx, value in enumerate(high_pair) if value == max(high_pair)]
                        low_pair_tied = [low_pair[i] for i in low_pair_tied_index]
                        if len(low_pair_tied) == len(set(low_pair_tied)):
                            winning_hands = [hands_to_compare[low_pair_tied_index[low_pair_tied.index(max(low_pair_tied))]]]
                            winning_players = [players[best_rank_index[low_pair_tied_index[low_pair_tied.index(max(low_pair_tied))]]]]
                        else:
                            high_single_tied_index = [idx for idx, value in enumerate(low_pair) if value == max(low_pair_tied) and idx in low_pair_tied_index]
                            high_single_tied = [high_single[i] for i in high_single_tied_index]
                            if len(high_single_tied) == len(set(high_single_tied)):
                                winning_hands = [hands_to_compare[high_single_tied_index[high_single_tied.index(max(high_single_tied))]]]
                                winning_players = [players[best_rank_index[high_single_tied_index[high_single_tied.index(max(high_single_tied))]]]]
                            else:
                                winning_index = [idx for idx, value in enumerate(high_single) if value == max(high_single_tied) and idx in high_single_tied_index]
                                winning_hands = [hands_to_compare[i] for i in winning_index]
                                winning_players = [players[best_rank_index[i]] for i in winning_index]

            elif max(rank) == 4:
                high_triple = []
                high_single = []
                low_single = []
                for hand in hands_to_compare:
                    high_triple.append(hands.cards_dict.get(hand[0][:-1]))
                    high_single.append(hands.cards_dict.get(hand[3][:-1]))
                    low_single.append(hands.cards_dict.get(hand[4][:-1]))
                    if len(high_triple) == len(set(high_triple)):
                        winning_hands = [hands_to_compare[high_triple.index(max(high_triple))]]
                        winning_players = [players[best_rank_index[high_triple.index(max(high_triple))]]]
                    else:
                        high_single_tied_index = [idx for idx, value in enumerate(high_triple) if value == max(high_triple)]
                        high_single_tied = [high_single[i] for i in high_single_tied_index]
                        if len(high_single_tied) == len(set(high_single_tied)):
                            winning_hands = [hands_to_compare[high_single_tied_index[high_single_tied.index(max(high_single_tied))]]]
                            winning_players = [players[best_rank_index[high_single_tied_index[high_single_tied.index(max(high_single_tied))]]]]
                        else:
                            low_single_tied_index = [idx for idx, value in enumerate(high_single) if value == max(high_single_tied) and idx in high_single_tied_index]
                            low_single_tied = [low_single[i] for i in low_single_tied_index]
                            if len(low_single_tied) == len(set(low_single_tied)):
                                winning_hands = [hands_to_compare[low_single_tied_index[low_single_tied.index(max(low_single_tied))]]]
                                winning_players = [players[best_rank_index[low_single_tied_index[low_single_tied.index(max(low_single_tied))]]]]
                            else:
                                winning_index = [idx for idx, value in enumerate(low_single) if value == max(low_single_tied) and idx in low_single_tied_index]
                                winning_hands = [hands_to_compare[i] for i in winning_index]
                                winning_players = [players[best_rank_index[i]] for i in winning_index]

            elif max(rank) in [7, 8]:
                high_card = [hands.cards_dict.get(hand[0][:-1]) for hand in hands_to_compare]
                low_card = [hands.cards_dict.get(hand[4][:-1]) for hand in hands_to_compare]
                if len(high_card) == len(set(high_card)):
                    winning_hands = [hands_to_compare[high_card.index(max(high_card))]]
                    winning_players = [players[best_rank_index[high_card.index(max(high_card))]]]
                else:
                    tied_hands = [idx for idx, value in enumerate(high_card) if value  == max(high_card)]
                    low_card_tied = [low_card[i] for i in tied_hands]
                    if len(low_card_tied) == len(set(low_card_tied)):
                        winning_hands = [hands_to_compare[low_card_tied.index(max(low_card_tied))]]
                        winning_players = [players[best_rank_index[low_card_tied.index(max(low_card_tied))]]]
                    else:
                        winning_index = [idx for idx, value in enumerate(low_card) if value == max(low_card_tied) and idx in tied_hands]
                        winning_hands = [hands_to_compare[i] for i in winning_index]
                        winning_players = [players[best_rank_index[i]] for i in winning_index]
        else:
            try:
                winning_hands.append(best_hands[best_rank_index[0]])
                winning_players.append(players[best_rank_index[0]])
            except:
                print('error in code')
                print(initial_best_rank_index)
                print(best_hands)
                print(best_rank_index)

        table_cards = table_cards_dict['Flop'] + table_cards_dict['Turn'] + table_cards_dict['River']
        table_cards = hands.convert_hand(table_cards)
        if winning_hands[0] == table_cards:
            winning_players = [player for player in players if participate_dict.get(player) == True]
            winning_hands = table_cards
        print(best_hands[-1])
        print(winning_hands)
        print(winning_players)
        _ = input('')

        return((winning_hands, winning_players))

    def side_pot(players, participate_dict, wallet_dict, bet_dict, pot_value, side_pots):
        side_pot_participants_list = []
        participating_bets = [value for idx, value in enumerate(list(bet_dict.values())) if participate_dict.get(players[idx]) == True]
        non_participating_bets = [value for idx, value in enumerate(list(bet_dict.values())) if participate_dict.get(players[idx]) == False]
        unique_bets = sorted(list(set(list(participating_bets))))
        if len(unique_bets) == 1:
            pot_value = sum(list(bet_dict.values())) + pot_value
            return((pot_value, side_pots, side_pot_participants_list))
        else:
            for i in range(len(unique_bets)):
                if i == 0:
                    pot_value = pot_value + unique_bets[i] * list(participate_dict.values()).count(True) + sum(non_participating_bets)
                else:
                    side_pot_participants = [players[idx] for idx, value in enumerate(list(bet_dict.values())) if value >= unique_bets[i]]
                    side_pot_participants_list.append(side_pot_participants)
                    side_pots.append((unique_bets[i] - unique_bets[i-1])*len(side_pot_participants))
            return((pot_value, side_pots, side_pot_participants_list))

    def side_pot_payout(players, player_hands, table_cards, side_pot, side_pot_participants, participate_dict):
        rank, best_hands = hands.evaluate_hands(side_pot_participants, player_hands, table_cards)
        winning_hands, winning_players = game_mech.determine_winner(rank, best_hands, side_pot_participants, participate_dict, table_cards)
        return((winning_hands, winning_players, side_pot))

    def pot_payout(winning_players, winning_hands, wallet_dict, bet_dict, pot_value, side_pots, side_pot_participants_list, participate_dict, table_careds):
        if len(side_pots) == 0 and bet_dict.get(winning_players[0]) == max(list(bet_dict.values())):
            if len(winning_players) == 1:
                wallet_dict[winning_players[0]] = wallet_dict.get(winning_players[0]) + pot_value
                pot_value = 0
                side_pots = []
                aesthetics.display_winner(winning_hands, winning_players)
                return((wallet_dict, pot_value, side_pots))
            else:
                for player in winning_players:
                    wallet_dict[player] = wallet_dict.get(player) + int(pot_value/len(winning_players))
                pot_value = 0
                side_pots = []
                aesthetics.display_winner(winning_hands, winning_players)
                return((wallet_dict, pot_value, side_pots))
        else:
            for side_pot_participants, side_pot in zip(side_pot_participants_list, side_pots):
                print(side_pot_participants)
                print(side_pot)
                _ = input('')
                winning_hands_side_pot, winning_players_side_pot, side_pot = game_mech.side_pot_payout(players, player_hands, table_cards, side_pot, side_pot_participants, participate_dict)
                if len(winning_players_side_pot) == 1:
                    wallet_dict[winning_players_side_pot[0]] = wallet_dict.get(winning_players_side_pot[0]) + side_pot
                else:
                    for player in winning_players_side_pot:
                        wallet_dict[player] = wallet_dict.get(player) + int(side_pot/len(winning_players_side_pot))
                print('Side pot value:', side_pot)
                aesthetics.display_winner(winning_hands_side_pot, winning_players_side_pot)
            if len(winning_players) == 1:
                wallet_dict[winning_players[0]] = wallet_dict.get(winning_players[0]) + pot_value
                pot_value = 0
                side_pots = []
                aesthetics.display_winner(winning_hands, winning_players)
                return((wallet_dict, pot_value, side_pots))
            else:
                for player in winning_players:
                    wallet_dict[player] = wallet_dict.get(player) + int(pot_value/len(winning_players))
                pot_value = 0
                side_pots = []
                aesthetics.display_winner(winning_hands, winning_players)
                return((wallet_dict, pot_value, side_pots))

    def check_game_end(players, wallet_dict, participate_dict, game_cont):
        for player in players:
            if wallet_dict.get(player) == 0:
                participate_dict[player] = False
            else:
                participate_dict[player] = True
        if list(participate_dict.values()).count(True) == 1:
            game_cont = False
            return(players, wallet_dict, participate_dict, game_cont)
        elif participate_dict.get(players[-1]) == False:
            game_cont = False
            return(players, wallet_dict, participate_dict, game_cont)
        else:
            return(players, wallet_dict, participate_dict, game_cont)

    def edit_players(players, participate_dict):
        players = [player for player in players if participate_dict.get(player) == True]
        return(players)


class hands:
    hands_dict = {'Pair': ('1a', '1b', '2*', '3*', '4*'), 'Two Pair': ('1a', '1b', '2a', '2b', '3*'),
                            'Three of a Kind': ('1a', '1b', '1c', '2*', '3*'), 'Straight': ('1*', '2*', '3*', '4*', '5*'),
                            'Flush': ('1a', '2a', '3a', '4a', '5a'), 'Full House': ('1a', '1b', '1c', '2a', '2b'),
                            'Four of a Kind': ('1a', '1b', '1c', '1d', '2*')}

    cards_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

    card_suit_ph = ['a', 'b', 'c', 'd']

    best_hands_dict = {'High Card': 1, 'Pair': 2, 'Two Pair': 3, 'Three of a Kind': 4, 'Straight': 5, 'Flush': 6, 'Full House': 7,
                       'Four of a Kind': 8, 'Straight Flush': 9, 'Royal Flush': 10}

    def check_straight_flush(hand):
        numbers = []
        for card in hand:
            numbers.append(hands.cards_dict.get(card[:-1]))
        return sorted(numbers) == list(range(min(numbers), max(numbers) + 1))

    def check_royal_flush(hand):
        numbers = []
        for card in hand:
            numbers.append(hands.cards_dict.get(card[:-1]))
        if sorted(numbers)[0] == 10 and sorted(numbers)[0] == 14:
            return(True)
        else:
            return(False)

    def convert_hand(hand):
        placeholder = False
        card_nums = []
        suits = []
        converted_hand = []
        converted_hands = []
        spliced_hand = []
        for card in hand:
            card_nums.append(hands.cards_dict.get(card[:-1]))
            suits.append(card[-1])

        sorted_card_nums, sorted_suits = zip(*sorted(zip(card_nums, suits), reverse = True))
        nums_count = [card_nums.count(i) for i in card_nums]
        suits_count = [suits.count(i) for i in suits]

        if 2 in nums_count or 3 in nums_count or 4 in nums_count:
            nums_count, card_nums_sorted = zip(*sorted(zip(nums_count, card_nums), reverse = True))
            unique_count, unique_nums = list(zip(*sorted(set(zip(nums_count, card_nums_sorted)), reverse = True)))
            for count, num in zip(unique_count, unique_nums):
                card_num_index = [idx for idx, value in enumerate(card_nums) if value == num]
                for idx in card_num_index:
                    spliced_hand.append(hand[idx])
                    if len(spliced_hand) == 5: break
                if count > 1 and len(converted_hand) < 4:
                    for i in range(1, count+1):
                        converted_hand.append(str(unique_nums.index(num)+1) + hands.card_suit_ph[i-1])
                        if len(converted_hand) == 5: break
                else:
                    converted_hand.append(str(unique_nums.index(num)+1) + '*')
                if len(converted_hand) == 5:
                    converted_hands.append((tuple(converted_hand), hand, tuple(spliced_hand)))
                    placeholder = True
                    converted_hand = []
                    spliced_hand = []
                    break
            if len(converted_hand) < 5:
                for i in range(len(converted_hand) + 1, 6):
                    converted_hand.append(str(i)+'*')

        if 5 in suits_count or 6 in suits_count or 7 in suits_count:
            suits_count, suits_sorted = list(zip(*sorted(zip(suits_count, suits), reverse = True)))
            for idx, suit in enumerate(suits_sorted):
                converted_hand.append(str(idx+1) + 'a')
                if len(converted_hand) == 5:
                    suit_index = [idx for idx, value in enumerate(suits) if value == suit]
                    spliced_nums, spliced_hand = list(zip(*sorted(zip([card_nums[idx] for idx in suit_index], [hand[idx] for idx in suit_index]))))[:6]
                    converted_hands.append((tuple(converted_hand), hand, spliced_hand))
                    placeholder = True
                    converted_hand = []
                    spliced_hand = []
                    break

        if (sorted_card_nums[0] - sorted_card_nums[-3]) == 4 or (sorted_card_nums[1] - sorted_card_nums[-2]) == 4 or (sorted_card_nums[2] - sorted_card_nums[-1]) == 4:
            if tuple(range(sorted_card_nums[0], sorted_card_nums[-3] - 1, -1)) == sorted_card_nums[:-2]:
                straight = sorted_card_nums[:-2]
                converted_hand = tuple([str(i) + '*' for i in range(1, 6)])
                for num in straight:
                    spliced_hand.append(hand[card_nums.index(num)])
            elif tuple(range(sorted_card_nums[1], sorted_card_nums[-2] - 1, -1)) == sorted_card_nums[1:-1]:
                straight = sorted_card_nums[1:-1]
                converted_hand = tuple([str(i) + '*' for i in range(1, 6)])
                for num in straight:
                    spliced_hand.append(hand[card_nums.index(num)])
            elif tuple(range(sorted_card_nums[2], sorted_card_nums[-1] - 1, -1)) == sorted_card_nums[2:]:
                straight = sorted_card_nums[2:]
                converted_hand = tuple([str(i) + '*' for i in range(1, 6)])
                for num in straight:
                    spliced_hand.append(hand[card_nums.index(num)])
            converted_hands.append((converted_hand, hand, tuple(spliced_hand)))
            placeholder = True
            spliced_hand = []
            converted_hand = []

        if placeholder == False:
            for num in sorted_card_nums[:5]:
                spliced_hand.append(hand[card_nums.index(num)])
            converted_hands.append(('High Card', hand, tuple(spliced_hand)))
            spliced_hand = []

        return(converted_hands)

    def get_hand(converted_hand, spliced_hand):
        for key, value in hands.hands_dict.items():
            if converted_hand == 'High Card':
                return('High Card')
            elif value == converted_hand:
                if key == 'Flush':
                    if hands.check_straight_flush(spliced_hand) == True:
                        if hands.check_royal_flush(spliced_hand) == True: return('Royal Flush')
                        else: return('Straight Flush')
                    else:
                        return(key)
                else: return(key)

    def find_best_hand(converted_hands):
        hand_rank = []
        for converted_hand, hand, spliced_hand in converted_hands:
            if type(hands.best_hands_dict.get(hands.get_hand(converted_hand, spliced_hand))) != int:
                hand_rank.append(0)
            else:
                hand_rank.append(hands.best_hands_dict.get(hands.get_hand(converted_hand, spliced_hand)))
        return((converted_hands[hand_rank.index(max(hand_rank))][2],
            hands.get_hand(converted_hands[hand_rank.index(max(hand_rank))][0], converted_hands[hand_rank.index(max(hand_rank))][2])))

    def evaluate_hands(players, player_hands, table_cards_dict):
        rank = []
        best_hands = []
        for player in players:
            try:
                hand = player_hands[player] + table_cards_dict['Flop'] + table_cards_dict['Turn'] + table_cards_dict['River']
            except:
                print(player)
                print(player_hands[player])
                print(table_cards_dict['Flop'])
                print(table_cards_dict['Turn'])
                print(table_cards_dict['River'])
                _ = input('')
            converted_hands = hands.convert_hand(hand)
            best_hand, hand_name = hands.find_best_hand(converted_hands)
            rank.append(hands.best_hands_dict.get(hand_name))
            best_hands.append(best_hand)
        return((rank, best_hands))

class aesthetics:

    def display_players(players, dealer, bb, lb, wallet_dict, bet_dict, pot_value, side_pots):
        os.system('cls')
        max_len_player_name = max([len(player) for player in players])
        print('Player', ' '*(max_len_player_name - 6), 'Wallet ', 'Bet   ', 'Role')
        for player in players:
            name_len = len(player)
            if player == dealer:
                print(player, ' '*(max_len_player_name - name_len), wallet_dict.get(player), ' '*(6-len(str(wallet_dict.get(player)))), bet_dict.get(player), ' '*(5 - len(str(bet_dict.get(player)))), 'Dealer')
            elif player == bb:
                print(player, ' '*(max_len_player_name - name_len),  wallet_dict.get(player),' '*(6-len(str(wallet_dict.get(player)))), bet_dict.get(player),' '*(5 - len(str(bet_dict.get(player)))), 'Big Blind')
            elif player == lb:
                print(player, ' '*(max_len_player_name - name_len),  wallet_dict.get(player),' '*(6-len(str(wallet_dict.get(player)))), bet_dict.get(player),' '*(5 - len(str(bet_dict.get(player)))), 'Little Blind')
            else:
                print(player, ' '*(max_len_player_name - name_len),  wallet_dict.get(player),' '*(6-len(str(wallet_dict.get(player)))), bet_dict.get(player),' '*(5 - len(str(bet_dict.get(player)))))
        if len(side_pots) >= 1:
            print('\nPot Value:', pot_value)
            for side_pot in side_pots:
                print('Side Pot', str(side_pots.index(side_pot) +1), 'Value:', side_pot)
        else:
            print('\nPot Value:', pot_value)

    '''fix display aesthetics for any hands having a 10'''
    def display_hand_initial(players, player_hands):
        'Your hand: is 11 spaces'
        print('           ', '----    ----\nYour Hand: |', player_hands.get(players[-1])[0], '|  |', player_hands.get(players[-1])[1],
               '|\n            ----    ----')

    def display_hand_flop(table_cards_dict):
        print('\n\n  ----      ----   ----   ----\n |    |    |', table_cards_dict.get('Flop')[0],
              '| |', table_cards_dict.get('Flop')[1],'| |', table_cards_dict.get('Flop')[2],
                '|\n  ----      ----   ----   ----')
        _ = input('')

    def display_hand_turn(table_cards_dict):
        print('\n\n  ----      ----   ----   ----   ----\n |    |    |', table_cards_dict.get('Flop')[0],
              '| |', table_cards_dict.get('Flop')[1],'| |', table_cards_dict.get('Flop')[2],
                '| |', table_cards_dict.get('Turn')[0], '|\n  ----      ----   ----   ----   ----')
        _ = input('')

    def display_hand_river(table_cards_dict):
        print('\n\n  ----      ----   ----   ----   ----   ----\n |    |    |', table_cards_dict.get('Flop')[0],
              '| |', table_cards_dict.get('Flop')[1],'| |', table_cards_dict.get('Flop')[2],
                '| |', table_cards_dict.get('Turn')[0], '| |', table_cards_dict.get('River')[0], '|\n  ----      ----   ----   ----   ----   ----')
        _ = input('')

    def display_winner(winning_hands, winning_players):
        if len(winning_players) == 1:
            print('Winning hand:', winning_hands[0])
            print('Winning Player:', winning_players[0])
            _ = input('')
        else:
            print('There was a tie. Winning hands:')
            for hand in winning_hands:
                print(hand)
            print('Winning Players:')
            for player in winning_players:
                print(player)
            _ = input('')

    def game_end(players, wallet_dict, participate_dict, turn):
        if participate_dict.get(players[-1]) == True:
            print('You win!')
            print('Turns to win:', turn)
        else:
            winning_player = players[list(wallet_dict.values()).index(max(list(wallet_dict.values())))]
            print('You lose.')
            print('Winning Player:', winning_player)
            print('Turns played:', turn)

class probabilities:

    def initial_hand(turn, num_players, player, participate_dict, player_hand, table_cards, dealt_deck):
        card_nums = []
        suits = []
        if len(table_cards) != 0:
            burn_num = len(table_cards.get('Burn'))
            hand = [card for card in player_hand]
            for key, value in table_cards.items():
                hand.append(value)
        else:
            burn_num = 0
            hand = player_hand
        for card in hand:
            card_nums.append(hands.cards_dict.get(card[:-1]))
            suits.append(card[-1])

        possible_turn = ['Initial', 'Flop', 'Turn', 'River']
        if participate_dict.get(player) == False:
            return()
        possible_hands_col = [key for key, value in hands.best_hands_dict.items()][::-1]
        single_card_prob_matrix = probabilities.single_card_prob_matrix(hand, turn, possible_turn)
        probability_df = pd.DataFrame(index = possible_turn, columns = possible_hands_col)
        for hand_to_calc in possible_hands_col:
            probability = probabilities.choose_probability_calc(hand, hand_to_calc, turn, possible_turn, num_players, player, card_nums, suits, table_cards, dealt_deck, single_card_prob_matrix)

        'https://pi.math.cornell.edu/~mec/2006-2007/Probability/Texasholdem.pdf'
        return()

    def single_card_prob_matrix(hand, turn, possible_turn):
        if turn == 'Initial':
            cards_left_to_deal = 5
        else:
            cards_left_to_deal = 3 - possible_turn.index(turn)
        column_headers = [key for key, value in hands.cards_dict.items()]
        rows = ['S', 'H', 'D', 'C']
        prob_matrix = pd.DataFrame(index = rows, columns = column_headers)
        for idx, row in prob_matrix.iterrows():
            for card_num in row.index:
                if card_num+idx in hand:
                    prob_matrix.at[idx, card_num] = 1
                else:
                    prob_matrix.at[idx, card_num] = cards_left_to_deal / (52 - len(hand))
        return(prob_matrix)

    def single_card_prob_matrix_for_flop(hand, flop_dealt):
        cards_left_to_deal = 5 - flop_dealt
        column_headers = [key for key, value in hands.cards_dict.items()]
        rows = ['S', 'H', 'D', 'C']
        prob_matrix = pd.DataFrame(index = rows, columns = column_headers)
        for idx, row in prob_matrix.iterrows():
            for card_num in row.index:
                if card_num+idx in hand:
                    prob_matrix.at[idx, card_num] = 1
                else:
                    prob_matrix.at[idx, card_num] = cards_left_to_deal / (52 - len(hand))
        return(prob_matrix)

    def choose_probability_calc(hand, hand_to_calc, turn, possible_turn, num_players, player, card_nums, suits, table_cards, dealt_deck, single_card_prob_matrix):
        '''player hands is a dict. we want to pass the single player's hand (as a list) into these functions. table_cards is also a dict with key
        as flop, turn, river. dealt_deck is a list. Turn indicates Initial, Flop, Turn, River'''
        if hand_to_calc == 'Royal Flush':
            probability = probabilities.royal_flush_calc(hand, num_players, card_nums, suits, table_cards, dealt_deck, single_card_prob_matrix, turn, possible_turn)

    def royal_flush_calc(hand, num_players, card_nums, suits, table_cards, dealt_deck, single_card_prob_matrix, turn, possible_turn):
        card_nums_needed = [14, 13, 12, 11, 10]
        cards_left = 7 - len(card_nums)
        num_remaining = len(dealt_deck)
        dealt_cards = 2*(num_players - 1)

        suits_acquired = [value for idx, value in enumerate(suits) if card_nums[idx] in card_nums_needed]
        card_index = [idx for idx, value in enumerate(suits) if value in suits_acquired and card_nums[idx] in card_nums_needed]
        potential_cards_needed = []
        for suit in list(set(suits_acquired)):
            target_hand = [key+suit for key, value in hands.cards_dict.items() if value in card_nums_needed]
            cards_nums_in_suit = [value for idx, value in enumerate(card_nums) if idx in card_index and suits[idx] == suit]
            target_hand_acquired = [key+suit for key, value in hands.cards_dict.items() if value in cards_nums_in_suit]
            potential_cards_needed.append([card for card in target_hand if card not in target_hand_acquired])
        nums_needed = 7
        cards_needed_in_best_hand = []
        for potential_hand in potential_cards_needed:
            if len(potential_hand) < nums_needed:
                nums_needed = len(potential_hand)
                cards_needed_in_best_hand = potential_hand
        if nums_needed == 0:
            probability = 1
            return(probability)
        elif nums_needed > cards_left:
            probability = 0
            return(probability)

        card_nums_needed = [hands.cards_dict.get(card[:-1]) for card in cards_needed_in_best_hand]
        suit_needed = cards_needed_in_best_hand[0][-1]


        '''below code has issues. If the cards needed is less than the number of cards left to be dealt, my odds of getting the hand i
        want greatly increases. I believe the below only accounts for the odds of getting the hand I want assuming the cards needed
        and the cards left to be dealt are equal'''
        if cards_left == len(card_nums_needed):
            if turn != 'Initial':
                probability_of_hand_list = []
                for card in cards_needed_in_best_hand[:-1]:
                    target_index = card[-1]
                    target_column = card[:-1]
                    next_turn = possible_turn[possible_turn.index(turn) + 1]
                    probability_of_hand_list.append(single_card_prob_matrix.at[target_index, target_column])
                    hand.append(card)
                    single_card_prob_matrix = probabilities.single_card_prob_matrix(hand, next_turn, possible_turn)
                probability_of_hand_list.append(single_card_prob_matrix.at[cards_needed_in_best_hand[-1][-1], cards_needed_in_best_hand[-1][:-1]])
                probability = np.prod(probability_of_hand_list)*len(cards_needed_in_best_hand)
                return(probability)

            else:
                probability_of_hand_list = []
                for card in cards_needed_in_best_hand[:3]:
                    target_index = card[-1]
                    target_column = card[:-1]
                    probability_of_hand_list.append(single_card_prob_matrix.at[target_index, target_column])
                    hand.append(card)
                    single_card_prob_matrix = probabilities.single_card_prob_matrix_for_flop(hand, 3 - (cards_needed_in_best_hand.index(card) + 1))
                probability = np.prod(probability_of_hand_list)*3
                probability_of_hand_list = [probability]




        return()


if __name__ == "__main__":
    np.random.RandomState(datetime.datetime.now().date().toordinal())
    turn = 0
    game_params = game_param
    game_mechs = game_mech
    num_players = game_mech.game_start() + 1

    '''players = ['Player ' + str(i+1) for i in range(num_players)]'''
    players = game_params.player_names(num_players)
    original_players = players

    game_cont = True
    previous_dealer = players[0]
    previous_players = players
    wallet_dict = game_param.player_wallets_initial(players, game_params.initial_money)
    participate_dict = {}
    for player in players:
        participate_dict[player] = True

    while game_cont == True:
        dealer, bb, lb, previous_dealer, previous_players = game_param.designate_players(players, turn, participate_dict, previous_players, previous_dealer, original_players)
        players_ordered = game_mech.define_turn_order(players, dealer, lb, bb)

        wallet_dict, bet_dict, blind_pot_value = game_mech.blind_bet(players, wallet_dict, lb, bb)

        side_pots = []
        side_pot_participants_list = []
        table_cards = {}
        aesthetics.display_players(players, dealer, bb, lb, wallet_dict, bet_dict, blind_pot_value, side_pots)

        shuffled_deck = game_mech.shuffle_deck()
        player_hands, dealt_deck = game_mech.deal_cards_players(players, shuffled_deck, participate_dict)
        aesthetics.display_hand_initial(players, player_hands)
        pot_value = 0
        wallet_dict, bet_dict, participate_dict, pot_value, side_pots, side_pot_participants_list = game_mech.bet_loop(players, wallet_dict, bet_dict, participate_dict, players_ordered, pot_value, side_pots, side_pot_participants_list)
        'pot_value, side_pots, side_pot_participants_list = game_mech.side_pot(players, participate_dict, wallet_dict, bet_dict, pot_value, side_pots)'

        table_cards, dealt_deck = game_mech.deal_flop(dealt_deck)
        for key, value in bet_dict.items():
            bet_dict[key] = 0
        aesthetics.display_players(players, dealer, bb, lb, wallet_dict, bet_dict, pot_value, side_pots)
        aesthetics.display_hand_initial(players, player_hands)
        aesthetics.display_hand_flop(table_cards)
        wallet_dict, bet_dict, participate_dict, pot_value, side_pots, side_pot_participants_list = game_mech.bet_loop(players, wallet_dict, bet_dict, participate_dict, players_ordered, pot_value, side_pots, side_pot_participants_list)
        'pot_value, side_pots, side_pot_participants_list = game_mech.side_pot(players, participate_dict, wallet_dict, bet_dict, pot_value, side_pots)'

        table_cards, dealt_deck = game_mech.deal_turn(table_cards, dealt_deck)
        for key, value in bet_dict.items():
            bet_dict[key] = 0
        aesthetics.display_players(players, dealer, bb, lb, wallet_dict, bet_dict, pot_value, side_pots)
        aesthetics.display_hand_initial(players, player_hands)
        aesthetics.display_hand_turn(table_cards)
        wallet_dict, bet_dict, participate_dict, pot_value, side_pots, side_pot_participants_list = game_mech.bet_loop(players, wallet_dict, bet_dict, participate_dict, players_ordered, pot_value, side_pots, side_pot_participants_list)
        'pot_value, side_pots, side_pot_participants_list = game_mech.side_pot(players, participate_dict, wallet_dict, bet_dict, pot_value, side_pots)'

        table_cards, dealt_deck = game_mech.deal_river(table_cards, dealt_deck)
        for key, value in bet_dict.items():
            bet_dict[key] = 0
        aesthetics.display_players(players, dealer, bb, lb, wallet_dict, bet_dict, pot_value, side_pots)
        aesthetics.display_hand_initial(players, player_hands)
        aesthetics.display_hand_river(table_cards)
        wallet_dict, bet_dict, participate_dict, pot_value, side_pots, side_pot_participants_list = game_mech.bet_loop(players, wallet_dict, bet_dict, participate_dict, players_ordered, pot_value, side_pots, side_pot_participants_list)
        '''last else in get_user_bet displays move dict, wallet, and bet for user if call or knock are chosen'''
        rank, best_hands = hands.evaluate_hands(players, player_hands, table_cards)
        winning_hands, winning_players = game_mech.determine_winner(rank, best_hands, players, participate_dict, table_cards)
        wallet_dict, pot_value, side_pots = game_mech.pot_payout(winning_players, winning_hands, wallet_dict, bet_dict, pot_value, side_pots, side_pot_participants_list, participate_dict, table_cards)
        players, wallet_dict, participate_dict, game_cont = game_mech.check_game_end(players, wallet_dict, participate_dict, game_cont)
        players = game_mech.edit_players(players, participate_dict)
        turn = turn + 1

    os.system('cls')
    aesthetics.game_end(original_players, wallet_dict, participate_dict, turn)
