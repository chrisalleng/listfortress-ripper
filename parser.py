import json
from dataclasses import dataclass


@dataclass
class Game:
    date: str
    player1: int
    player2: int
    winner: int


@dataclass
class Player:
    points: int
    max_i: int


@dataclass
class Result:
    date: str
    last_move_win: bool


def get_matches():
    matches = 0
    games = []
    players = [None] * 100000
    with open('merged_file.json') as json_file:
        data = json.load(json_file)
        for tournament in data:
            for player in tournament['participants']:
                player_id = player['id']
                player_list = player['list_json']
                players[player_id] = player_list
            for rounds in tournament['rounds']:
                # if rounds['roundtype_id'] == 2:
                for match in rounds['matches']:
                    matches += 1
                    games.append(Game(tournament['date'],
                                      match['player1_id'],
                                      match['player2_id'],
                                      match['winner_id']))
        print(str(matches) + ' matches parsed')
        return players, games


def get_max_i_bid(player_list, all_prices):
    try:
        parsed = json.loads(player_list)
    except ValueError as e:
        return 201, 7
    max_i = 0
    if 'points' not in parsed:
        points = 201
        max_i = 7
        return points, max_i
    else:
        points = parsed['points']
        for pilot in parsed['pilots']:
            for card in all_prices:
                card_id = card['xws']
                if card_id in aces:
                    if card_id == pilot['id']:
                        initiative = card['initiative']
                        if max_i < initiative:
                            max_i = initiative
                            if max_i == 6:
                                return points, max_i
    return points, max_i


aces = ['lukeskywalker', 'rexlerbrath', 'redline', 'whisper', 'duchess', 'darthvader', 'fennrau', 'oldteroch',
        'hansolo', 'bobafett', 'wedgeantilles', 'anakinskywalker', 'soontirfel', 'poedameron', 'quickdraw',
        'lulolampar','tallissanlintra', 'rey', 'niennunb', 'elloasty', 'kyloren', 'blackout', 'obiwankenobi',
        'plokoon']
# aces = ['anakinskywalker', 'soontirfel', 'poedameron']

with open('static/costs.json') as json_file:
    full_prices = json.load(json_file)
all_lists, all_games = get_matches()
list_details = [None] * 100000
for player_id, current_list in enumerate(all_lists):
    if current_list is not None:
        print(player_id)
        player_points, max_player_i = get_max_i_bid(current_list, full_prices)
        list_details[player_id] = Player(player_points, max_player_i)
final_results = []
for game in all_games:
    if game.player1 is None or game.player2 is None or list_details[game.player1] is None or list_details[
            game.player2] is None:
        continue
    if (list_details[game.player1].max_i == 7
            or list_details[game.player2].max_i == 7
            or list_details[game.player1].points == 201
            or list_details[game.player2].points == 201
            or list_details[game.player1].points is None
            or list_details[game.player2].points is None
            or list_details[game.player1].max_i < 5
            or list_details[game.player2].max_i < 5
        ):
        continue
    # Result(date,bool last_move_win)
    player1id = game.player1
    player1points = list_details[game.player1].points
    player1maxi = list_details[game.player1].max_i
    player2id = game.player2
    player2points = list_details[game.player2].points
    player2maxi = list_details[game.player2].max_i
    if list_details[game.player1].max_i > list_details[game.player2].max_i:
        p1_move_last = True
    elif list_details[game.player1].max_i < list_details[game.player2].max_i:
        p1_move_last = False
    elif list_details[game.player1].points < list_details[game.player2].points:
        p1_move_last = True
    elif list_details[game.player1].points > list_details[game.player2].points:
        p1_move_last = False
    else:
        continue
    game_winner = game.winner
    if(p1_move_last and game.winner == game.player1) or (not p1_move_last and game.winner == game.player2):
        last_moving_player_won = True
    else:
        last_moving_player_won = False
    final_results.append(Result(game.date, last_moving_player_won))

final_sum = 0
for result in final_results:
    if result.last_move_win:
        final_sum += 1
average = final_sum / len(final_results)
print(average)
print(str(len(final_results)) + " matches")
