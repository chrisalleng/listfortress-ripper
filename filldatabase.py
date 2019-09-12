import json
import mysql.connector
import requests


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

    input_cursor.execute("DROP TABLE IF EXISTS faction_ref")
    input_cursor.execute("CREATE TABLE faction_ref ("
                         "faction_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "name VARCHAR(255), "
                         "xws VARCHAR(255))")

    input_cursor.execute("DROP TABLE IF EXISTS ship_ref")
    input_cursor.execute("CREATE TABLE ship_ref ("
                         "ship_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "ship_name VARCHAR(255))")

    input_cursor.execute("DROP TABLE IF EXISTS pilot_ref")
    input_cursor.execute("CREATE TABLE pilot_ref ("
                         "pilot_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "name VARCHAR(255), "
                         "cost INT,"
                         "ship_id INT,"
                         "initiative INT,"
                         "xws VARCHAR(255))")

    input_cursor.execute("DROP TABLE IF EXISTS upgrade_ref")
    input_cursor.execute("CREATE TABLE upgrade_ref ("
                         "upgrade_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "name VARCHAR(255), "
                         "cost INT,"
                         "xws VARCHAR(255))")


def get_ref_data():
    pilots_url = 'http://xhud.sirjorj.com/xwing.cgi/pilots2?format=json'
    pilots_response = requests.get(pilots_url)

    upgrades_url = 'http://xhud.sirjorj.com/xwing.cgi/upgrades2?format=json'
    upgrades_response = requests.get(upgrades_url)

    parsed_pilots = json.loads(pilots_response.content.decode('utf-8'))
    parsed_upgrades = json.loads(upgrades_response.content.decode('utf-8'))

    ships = {}
    pilots = {}
    upgrades = {}

    for parsed_pilot in parsed_pilots:
        pilot_name = parsed_pilot['name']
        pilot_xws = parsed_pilot['xws']
        pilot_cost = parsed_pilot['cost']
        if pilot_cost == "???":
            continue
        pilot_initiative = parsed_pilot['initiative']
        ship = parsed_pilot['ship']

        if ship not in ships:
            ships[ship] = (ship, len(ships) + 1)
        pilots[pilot_xws] = (pilot_name, pilot_xws, pilot_cost, pilot_initiative, ships[ship][1])

    for parsed_upgrade in parsed_upgrades:
        upgrade_name = parsed_upgrade['name']
        upgrade_xws = parsed_upgrade['xws']
        if 'cost' in parsed_upgrade:
            if parsed_upgrade['cost']['variable'] == "None":
                upgrade_cost = parsed_upgrade['cost']['value']
            elif parsed_upgrade['cost']['variable'] == "initiative":
                upgrade_cost = parsed_upgrade['cost']['6']
            elif parsed_upgrade['cost']['variable'] == "Agility":
                upgrade_cost = parsed_upgrade['cost']['agi3']
            elif parsed_upgrade['cost']['variable'] == "BaseSize":
                upgrade_cost = parsed_upgrade['cost']['large']
            else:
                upgrade_cost = 200
        else:
            upgrade_cost = 0

        upgrades[upgrade_name] = (upgrade_name, upgrade_xws, upgrade_cost)

    return ships, pilots, upgrades


def update_tables(filename):
    with open(filename) as json_file:
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
                                pilot_upgrades = pilot['upgrades'].items()
                                for key, value in pilot_upgrades:
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
                    values = (
                        match_id, player1_id, player1_points, player2_id, player2_points, winner_id, match_type, date)
                    cursor.execute(sql, values)


database = mysql.connector.connect(
    host="localhost",
    user="listfortress_ripper",
    password="password",
    database="listfortress",
    auth_plugin='mysql_native_password'
)
cursor = database.cursor()
clear_tables(cursor)
ref_ships, ref_pilots, ref_upgrades = get_ref_data()

for ref_pilot in ref_pilots.items():
    ref_pilot = ref_pilot[1]
    sql = "INSERT INTO pilot_ref (name, xws, cost, initiative, ship_id ) " \
        " VALUES (%s, %s, %s, %s, %s) "
    cursor.execute(sql, ref_pilot)

for ref_ship in ref_ships.items():
    ref_ship = ref_ship[1]
    sql = "INSERT INTO ship_ref (ship_name, ship_id ) " \
          " VALUES (%s, %s) "
    cursor.execute(sql, ref_ship)

for ref_upgrade in ref_upgrades.items():
    ref_upgrade = ref_upgrade[1]
    sql = "INSERT INTO upgrade_ref (name, xws, cost ) " \
          " VALUES (%s, %s, %s) "
    cursor.execute(sql, ref_upgrade)

faction_sql = "INSERT INTO faction_ref (faction_id, name, xws) VALUES (%s, %s, %s)"
factions = [(1, "Rebel Alliance", "rebelalliance"),
            (2, "Galactic Empire", "galacticempire"),
            (3, "Scum And Villainy", "scumandvillainy"),
            (4, "Resistance", "resistance"),
            (5, "First Order", "firstorder"),
            (6, "Galactic Republic", "galacticrepublic"),
            (7, "Separatist Aliiance", "separatistalliance")]
cursor.executemany(faction_sql, factions)

update_tables('merged_file.json')
database.commit()
cursor.close()
database.close()
