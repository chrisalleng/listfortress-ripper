import json
from errno import errorcode

import mysql.connector


def clear_tables(input_cursor):
    input_cursor.execute("DROP TABLE IF EXISTS players")
    input_cursor.execute("CREATE TABLE players ("
                         "player_id INT AUTO_INCREMENT PRIMARY KEY, "
                         "faction VARCHAR(255), "
                         "points INT, "
                         "event_players INT, "
                         "event_format INT, "
                         "swiss_standing INT, "
                         "cut_standing INT)")

    input_cursor.execute("DROP TABLE IF EXISTS pilots")
    input_cursor.execute("CREATE TABLE pilots ("
                         "pilot_id INT AUTO_INCREMENT PRIMARY KEY, "
                         "player_id INT,"
                         "pilot VARCHAR(255))")

    input_cursor.execute("DROP TABLE IF EXISTS upgrades")
    input_cursor.execute("CREATE TABLE upgrades ("
                         "upgrade_id INT AUTO_INCREMENT PRIMARY KEY, "
                         "pilot_id INT,"
                         "upgrade VARCHAR(255))")

    input_cursor.execute("DROP TABLE IF EXISTS matches")
    input_cursor.execute("CREATE TABLE matches ("
                         "match_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "player1_id INT,"
                         "player1_points INT,"
                         "player2_id INT,"
                         "player2_points INT,"
                         "winner_id INT,"
                         "type INT,"
                         "date DATE)")


database = mysql.connector.connect(
    host="localhost",
    user="listfortress_ripper",
    password="password",
    database="listfortress",
    auth_plugin='mysql_native_password'
)
cursor = database.cursor()
clear_tables(cursor)

with open('merged_file.json') as json_file:
    data = json.load(json_file)
    for tournament in data:
        # Insert Players
        for player in tournament['participants']:
            if player['list_json'] is not None:
                try:
                    player_list = json.loads(player['list_json'])
                except ValueError as e:
                    continue
                if 'points' in player_list and player_list['points'] is not None and player_list['points'] is not 0:
                    player_id = player['id']
                    faction = player_list['faction']
                    points = player_list['points']
                    event_players = len(tournament['participants'])
                    event_format = tournament['format_id']
                    swiss_standing = player['swiss_rank']
                    cut_standing = player['top_cut_rank']

                    sql = "INSERT INTO players (player_id, faction, points, event_players, event_format, " \
                          "swiss_standing, cut_standing) VALUES (%s, %s, %s, %s, %s, %s, %s) "
                    values = (player_id, faction, points, event_players, event_format, swiss_standing, cut_standing)
                    if isinstance(points, int):
                        cursor.execute(sql, values)
                    else:
                        print(str(player_id) + " " + points)
                        continue

                    # Insert Pilots
                    for pilot in player_list['pilots']:
                        pilot_id = pilot['id']
                        sql = "INSERT INTO pilots (player_id, pilot) VALUES (%s, %s) "
                        values = (player_id, pilot_id)
                        cursor.execute(sql, values)
                        pilot_id = cursor.lastrowid

                        if 'upgrades' in pilot and len(pilot['upgrades']) > 0:

                            # Insert Upgrade
                            upgrades = pilot['upgrades'].items()
                            for key, value in upgrades:
                                upgrade_list = value
                                for upgrade in upgrade_list:
                                    sql = "INSERT INTO upgrades (pilot_id, upgrade) VALUES (%s, %s) "
                                    values = (pilot_id, upgrade)
                                    cursor.execute(sql, values)

        # Insert all matches
        for rounds in tournament['rounds']:
            for match in rounds['matches']:
                match_id = match['id']
                player1_id = match['player1_id']
                player1_points = match['player1_points']
                player2_id = match['player2_id']
                player2_points = match['player2_points']
                winner_id = match['winner_id']
                match_type = rounds['roundtype_id']
                date = tournament['date']

                sql = "INSERT INTO matches (match_id, player1_id, player1_points, player2_id, player2_points, " \
                      "winner_id, type, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                values = (match_id, player1_id, player1_points, player2_id, player2_points, winner_id, match_type, date)
                cursor.execute(sql, values)

    database.commit()
