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
    elif pilot_xws == "anakinskywalkerywing":
        pilot_xws = "anakinskywalker-btlbywing"

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
    input_cursor.execute("DROP TABLE IF EXISTS matches_players")
    input_cursor.execute("DROP TABLE IF EXISTS matches")
    input_cursor.execute("DROP TABLE IF EXISTS upgrades")
    input_cursor.execute("DROP TABLE IF EXISTS pilots")
    input_cursor.execute("DROP TABLE IF EXISTS players")
    input_cursor.execute("DROP TABLE IF EXISTS tournaments")
    input_cursor.execute("DROP TABLE IF EXISTS ref_pilot")
    input_cursor.execute("DROP TABLE IF EXISTS ref_ship")
    input_cursor.execute("DROP TABLE IF EXISTS ref_upgrade")
    input_cursor.execute("DROP TABLE IF EXISTS ref_faction")

    input_cursor.execute("CREATE TABLE ref_ship ("
                         "ship_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "ship_name VARCHAR(255))")

    input_cursor.execute("CREATE TABLE ref_pilot ("
                         "ref_pilot_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "ship_id INT,"
                         "name VARCHAR(255), "
                         "cost INT,"
                         "initiative INT,"
                         "xws VARCHAR(255),"
                         "FOREIGN KEY(ship_id) REFERENCES ref_ship(ship_id))")

    input_cursor.execute("CREATE TABLE ref_upgrade ("
                         "ref_upgrade_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "name VARCHAR(255), "
                         "cost INT,"
                         "xws VARCHAR(255))")

    input_cursor.execute("CREATE TABLE ref_faction ("
                         "faction_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "name VARCHAR(255), "
                         "xws VARCHAR(255))")

    input_cursor.execute("CREATE TABLE tournaments ("
                         "tournament_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "players INT, "
                         "format INT)")

    input_cursor.execute("CREATE TABLE players ("
                         "player_id INT AUTO_INCREMENT PRIMARY KEY, "
                         "tournament_id INT,"
                         "faction INT, "
                         "points INT, "
                         "swiss_standing INT, "
                         "cut_standing INT,"
                         "FOREIGN KEY(tournament_id) REFERENCES tournaments(tournament_id),"
                         "FOREIGN KEY(faction) REFERENCES ref_faction(faction_id))")

    input_cursor.execute("CREATE TABLE pilots ("
                         "pilot_id INT AUTO_INCREMENT PRIMARY KEY, "
                         "player_id INT,"
                         "points INT,"
                         "ref_pilot_id INT,"
                         "FOREIGN KEY(player_id) REFERENCES players(player_id),"
                         "FOREIGN KEY(ref_pilot_id) REFERENCES ref_pilot(ref_pilot_id))")

    input_cursor.execute("CREATE TABLE upgrades ("
                         "upgrade_id INT AUTO_INCREMENT PRIMARY KEY, "
                         "pilot_id INT,"
                         "ref_upgrade_id INT,"
                         "FOREIGN KEY(pilot_id) REFERENCES pilots(pilot_id),"
                         "FOREIGN KEY(ref_upgrade_id) REFERENCES ref_upgrade(ref_upgrade_id))")

    input_cursor.execute("CREATE TABLE matches ("
                         "match_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "winner_id INT,"
                         "type INT,"
                         "date DATE,"
                         "FOREIGN KEY(winner_id) REFERENCES players(player_id))")

    input_cursor.execute("CREATE TABLE matches_players ("
                         "entry_id INT AUTO_INCREMENT PRIMARY KEY,"
                         "match_id INT,"
                         "player_id INT,"
                         "player_points INT,"
                         "FOREIGN KEY(player_id) REFERENCES players(player_id),"
                         "FOREIGN KEY(match_id) REFERENCES matches(match_id))")


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
    all_ref_pilots = []
    for pilot in pilots.items():
        pilot = pilot[1]
        all_ref_pilots.append(pilot)

    all_ref_ships = []
    for ship in ships.items():
        ship = ship[1]
        all_ref_ships.append(ship)
    sql = "INSERT INTO ref_ship (ship_name, ship_id) " \
          " VALUES (%s, %s) "
    cursor.executemany(sql, all_ref_ships)

    sql = "INSERT INTO ref_pilot (name, xws, cost, initiative, ship_id, ref_pilot_id) " \
          " VALUES (%s, %s, %s, %s, %s, %s) "
    cursor.executemany(sql, all_ref_pilots)

    all_ref_upgrades = []
    for upgrade in upgrades.items():
        upgrade = upgrade[1]
        all_ref_upgrades.append(upgrade)
    sql = "INSERT INTO ref_upgrade (name, xws, cost, ref_upgrade_id) " \
          " VALUES (%s, %s, %s, %s) "
    cursor.executemany(sql, all_ref_upgrades)

    faction_sql = "INSERT INTO ref_faction (faction_id, name, xws) VALUES (%s, %s, %s)"
    factions_values = [(1, "Rebel Alliance", "rebelalliance"),
                (2, "Galactic Empire", "galacticempire"),
                (3, "Scum And Villainy", "scumandvillainy"),
                (4, "Resistance", "resistance"),
                (5, "First Order", "firstorder"),
                (6, "Galactic Republic", "galacticrepublic"),
                (7, "Separatist Alliance", "separatistalliance"),
                (8, "Unknown", "unknown")]
    cursor.executemany(faction_sql, factions_values)

    factions = {
    }

    for faction_value in factions_values:
        factions[faction_value[2]] = faction_value[0]
    return ships, pilots, upgrades, factions


def update_tables(pilots, upgrades, factions, filename):
    with open(filename) as json_file:
        data = json.load(json_file)
        all_pilots = []
        all_upgrades = []
        all_matches = []
        all_players = []
        all_players_matches = []
        all_tournaments = []
        pilot_id = 0
        for tournament in data:
            # Get Tournaments
            tournament_id = tournament['id']
            tournament_player_count = len(tournament['participants'])
            tournament_format = tournament['format_id']
            all_tournaments.append((tournament_id, tournament_player_count, tournament_format))

            # Get Players
            for player in tournament['participants']:
                if player['list_json'] is not None:
                    try:
                        player_list = json.loads(player['list_json'])
                    except ValueError as e:
                        pass
                if 'points' in player_list and player_list['points'] is not None and player_list['points'] is not 0\
                        and isinstance(player_list['points'], int):
                    points = player_list['points']
                else:
                    points = None
                player_id = player['id']
                if 'faction' in player_list:
                    faction = factions[player_list['faction']]
                else:
                    faction = 8
                swiss_standing = player['swiss_rank']
                cut_standing = player['top_cut_rank']

                values = (player_id, tournament_id, faction, points, swiss_standing, cut_standing)
                all_players.append(values)

                # Insert Pilots
                if 'pilots' in player_list:
                    for pilot in player_list['pilots']:
                        if 'id' in pilot:
                            xws = pilot['id']
                        else:
                            xws = pilot['name']
                        xws = clean_pilot_xws(xws)
                        ref_pilot_id = pilots[xws][5]
                        if 'points' in pilot and isinstance(pilot['points'], int):
                            points = pilot['points']
                        else:
                            points = None
                        pilot_id = pilot_id + 1
                        current_pilot = (player_id, ref_pilot_id, points)
                        all_pilots.append(current_pilot)

                        if 'upgrades' in pilot and len(pilot['upgrades']) > 0:
                            # Insert Upgrade
                            pilot_upgrades = pilot['upgrades'].items()
                            for key, value in pilot_upgrades:
                                upgrade_list = value
                                for upgrade in upgrade_list:
                                    upgrade = clean_upgrade_xws(upgrade)
                                    if upgrade == "skip":
                                        continue
                                    upgrade_id = upgrades[upgrade][3]
                                    current_upgrade = (pilot_id, upgrade_id)
                                    all_upgrades.append(current_upgrade)
            # Insert all matches

            for rounds in tournament['rounds']:
                for match in rounds['matches']:
                    match_id = match['id']
                    winner_id = match['winner_id']
                    match_type = rounds['roundtype_id']
                    date = tournament['date']
                    current_match = (match_id, winner_id, match_type, date)
                    all_matches.append(current_match)

                    player1_id = match['player1_id']
                    player1_points = match['player1_points']
                    current_player = (match_id, player1_id, player1_points)
                    all_players_matches.append(current_player)

                    player2_id = match['player2_id']
                    player2_points = match['player2_points']
                    current_player = (match_id, player2_id, player2_points)
                    all_players_matches.append(current_player)

        sql = "INSERT INTO tournaments (tournament_id, players, format) VALUES (%s, %s, %s) "
        cursor.executemany(sql, all_tournaments)

        sql = "INSERT INTO players (player_id, tournament_id, faction, points,  swiss_standing, cut_standing) " \
              "VALUES (%s, %s, %s, %s, %s, %s) "
        cursor.executemany(sql, all_players)

        sql = "INSERT INTO matches (match_id, winner_id, type, date) VALUES (%s, %s, %s, %s) "
        cursor.executemany(sql, all_matches)

        player_sql = "INSERT INTO matches_players (match_id, player_id, player_points) VALUES (%s, %s, %s)"
        cursor.executemany(player_sql, all_players_matches)

        sql = "INSERT INTO pilots (player_id, ref_pilot_id, points) VALUES (%s, %s, %s) "
        cursor.executemany(sql, all_pilots)

        sql = "INSERT INTO upgrades (pilot_id, ref_upgrade_id) VALUES (%s, %s) "
        cursor.executemany(sql, all_upgrades)


database = mysql.connector.connect(
    host="xwing.gateofstorms.net",
    user="brunas",
    password="scpLVgtx",
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
