import json
import requests
import os
import shutil


def get_all_events():
    api_url = 'https://listfortress.com/api/v1/tournaments/'

    response = requests.get(api_url)
    parsed = json.loads(response.content.decode('utf-8'))

    ids = []
    for event in parsed:
        ids.append(event['id'])
    return ids


def get_tournament(tournament_id):
    api_url = 'https://listfortress.com/api/v1/tournaments/' + str(tournament_id)

    response = requests.get(api_url)
    parsed = json.loads(response.content.decode('utf-8'))
    print(tournament_id)
    return parsed


if os.path.isdir('data'):
    shutil.rmtree('data')
os.mkdir('data')
listfortress_tournament_ids = get_all_events()
for tournament in listfortress_tournament_ids:
    parsedjson = get_tournament(tournament)
    with open('data/' + str(tournament) + '.json', 'w') as file:
        json.dump(parsedjson, file)
