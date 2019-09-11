import json
from errno import errorcode

import mysql.connector


def clear_tables(input_cursor):
    input_cursor.execute("DROP TABLE IF EXISTS players")
    input_cursor.execute("CREATE TABLE players (player_id INT AUTO_INCREMENT PRIMARY KEY, "
                         "faction VARCHAR(255), "
                         "points INT, "
                         "event_players INT, "
                         "event_format INT, "
                         "swiss_standing INT, "
                         "cut_standing INT)")

    input_cursor.execute("DROP TABLE IF EXISTS lists")
    input_cursor.execute("CREATE TABLE lists (pilot_id INT AUTO_INCREMENT PRIMARY KEY, "
                         "player_id INT,"
                         "pilot VARCHAR(255))")


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

                    for pilot in player_list['pilots']:
                        pilot_id = pilot['id']

                        sql = "INSERT INTO lists (player_id, pilot) VALUES (%s, %s) "
                        values = (player_id, pilot_id)
                        cursor.execute(sql, values)
    database.commit()
