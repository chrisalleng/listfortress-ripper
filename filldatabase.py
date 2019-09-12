import json
import mysql.connector
import requests


def clean_pilot_xws(pilot_xws):
    if pilot_xws == "niennumb-t70xwing":
        pilot_xws = "niennunb"
    elif pilot_xws == "oddballarc170":
        pilot_xws = "oddball-arc170starfighter"
    elif pilot_xws == "ricolie-nabooroyaln1starfighter":
        pilot_xws = "ricolie"

    return pilot_xws


def clean_upgrade_xws(upgrade_xws):
    if upgrade_xws == "hardpointcannon":
        upgrade_xws = "skip"
    elif upgrade_xws == "hardpointmissile":
        upgrade_xws = "skip"
    elif upgrade_xws == "hardpointtorpedo":
        upgrade_xws = "skip"
    elif upgrade_xws == "reysmilleniumfalcon":
        upgrade_xws = "reysmillenniumfalcon"
    elif upgrade_xws == "rey":
        upgrade_xws = "rey-gunner"
    elif upgrade_xws == "chewbaccaresistance":
        upgrade_xws = "chewbacca-crew-swz19"
    elif upgrade_xws == "leiaorganaresistance":
        upgrade_xws = "leiaorgana-resistance"
    return upgrade_xws


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
                         "entry_id INT AUTO_INCREMENT PRIMARY KEY, "
                         "pilot_id INT,"
                         "upgrade_id INT)")

    input_cursor.execute("DROP TABLE IF EXISTS matches")
    input_cursor.execute("CREATE TABLE matches ("
                         "match_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "winner_id INT,"
                         "type INT,"
                         "date DATE)")

    input_cursor.execute("DROP TABLE IF EXISTS matches_players")
    input_cursor.execute("CREATE TABLE matches_players ("
                         "entry_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "match_id INT,"
                         "player_id INT,"
                         "player_points INT)")

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
    pilot_id = 0
    upgrade_id = 0

    for parsed_pilot in parsed_pilots:
        pilot_name = parsed_pilot['name']
        pilot_xws = parsed_pilot['xws']
        pilot_cost = parsed_pilot['cost']
        pilot_id = pilot_id + 1
        if pilot_cost == "???":
            continue
        pilot_initiative = parsed_pilot['initiative']
        ship = parsed_pilot['ship']

        if ship not in ships:
            ships[ship] = (ship, len(ships) + 1)
        pilots[pilot_xws] = (pilot_name, pilot_xws, pilot_cost, pilot_initiative, ships[ship][1], pilot_id)

    for parsed_upgrade in parsed_upgrades:
        upgrade_name = parsed_upgrade['name']
        upgrade_xws = parsed_upgrade['xws']
        upgrade_id = upgrade_id + 1
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

        upgrades[upgrade_xws] = (upgrade_name, upgrade_xws, upgrade_cost, upgrade_id)

    for pilot in pilots.items():
        pilot = pilot[1]
        sql = "INSERT INTO pilot_ref (name, xws, cost, initiative, ship_id, pilot_id ) " \
              " VALUES (%s, %s, %s, %s, %s, %s) "
        cursor.execute(sql, pilot)

    for ship in ships.items():
        ship = ship[1]
        sql = "INSERT INTO ship_ref (ship_name, ship_id ) " \
              " VALUES (%s, %s) "
        cursor.execute(sql, ship)

    for upgrade in upgrades.items():
        upgrade = upgrade[1]
        sql = "INSERT INTO upgrade_ref (name, xws, cost, upgrade_id ) " \
              " VALUES (%s, %s, %s, %s) "
        cursor.execute(sql, upgrade)

    faction_sql = "INSERT INTO faction_ref (faction_id, name, xws) VALUES (%s, %s, %s)"
    factions_values = [(1, "Rebel Alliance", "rebelalliance"),
                (2, "Galactic Empire", "galacticempire"),
                (3, "Scum And Villainy", "scumandvillainy"),
                (4, "Resistance", "resistance"),
                (5, "First Order", "firstorder"),
                (6, "Galactic Republic", "galacticrepublic"),
                (7, "Separatist Alliance", "separatistalliance")]
    cursor.executemany(faction_sql, factions_values)

    factions = {
    }

    for faction_value in factions_values:
        factions[faction_value[2]] = factions_values[0]
    return ships, pilots, upgrades, factions


def update_tables(pilots, upgrades, factions, filename):
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
                        faction = factions[player_list['faction']][0]
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
                            xws = pilot['id']
                            xws = clean_pilot_xws(xws)
                            pilot_id = pilots[xws][5]
                            sql = "INSERT INTO pilots (player_id, pilot) VALUES (%s, %s) "
                            values = (player_id, pilot_id)
                            cursor.execute(sql, values)

                            if 'upgrades' in pilot and len(pilot['upgrades']) > 0:

                                # Insert Upgrade
                                pilot_upgrades = pilot['upgrades'].items()
                                for key, value in pilot_upgrades:
                                    upgrade_list = value
                                    for upgrade in upgrade_list:
                                        sql = "INSERT INTO upgrades (pilot_id, upgrade_id) VALUES (%s, %s) "
                                        upgrade = clean_upgrade_xws(upgrade)
                                        if upgrade == "skip":
                                            continue
                                        upgrade_id = upgrades[upgrade][3]
                                        values = (pilot_id, upgrade_id)
                                        cursor.execute(sql, values)

            # Insert all matches
            for rounds in tournament['rounds']:
                for match in rounds['matches']:
                    match_id = match['id']
                    winner_id = match['winner_id']
                    match_type = rounds['roundtype_id']
                    date = tournament['date']

                    sql = "INSERT INTO matches (match_id, winner_id, type, date) VALUES (%s, %s, %s, %s) "
                    values = (match_id, winner_id, match_type, date)
                    cursor.execute(sql, values)

                    player1_id = match['player1_id']
                    player1_points = match['player1_points']
                    player1_sql = "INSERT INTO matches_players (match_id, player_id, player_points) VALUES (%s, %s, %s)"
                    player1_values = (match_id, player1_id, player1_points)
                    cursor.execute(player1_sql, player1_values)

                    player2_id = match['player2_id']
                    player2_points = match['player2_points']
                    player2_sql = "INSERT INTO matches_players (match_id, player_id, player_points) VALUES (%s, %s, %s)"
                    player2_values = (match_id, player2_id, player2_points)
                    cursor.execute(player2_sql, player2_values)


database = mysql.connector.connect(
    host="localhost",
    user="listfortress_ripper",
    password="password",
    database="listfortress",
    auth_plugin='mysql_native_password'
)
cursor = database.cursor()
clear_tables(cursor)
ref_ships, ref_pilots, ref_upgrades, ref_factions = get_ref_data()
update_tables(ref_pilots, ref_upgrades, ref_factions, 'merged_file.json')
database.commit()
cursor.close()
database.close()
