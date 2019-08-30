import json
import requests
import os
import shutil


def get_tournament(tournamentid):
    api_url = 'https://listfortress.com/api/v1/tournaments/' + str(tournamentid)

    response = requests.get(api_url)
    parsed = json.loads(response.content.decode('utf-8'))
    print(tournamentid)
    return parsed


if os.path.isdir('data'):
    shutil.rmtree('data')
os.mkdir('data')
i = 0
fails = 0
while True:
    i += 1
    parsedjson = get_tournament(i)
    if 'errors' not in parsedjson:
        fails = 0
        with open('data/' + str(i) + '.json', 'w') as file:
            json.dump(parsedjson, file)
    else:
        fails += 1
        if fails > 100:
            break
