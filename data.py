import requests
import pprint
import json

import os
import time



def update_data():
    response = requests.get("https://api.scryfall.com/bulk-data/default_cards")
    response.raise_for_status()
    download_url = response.json()["download_uri"]
    file_name = "default-cards.json"
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)



def init_cards():
    with open("default-cards.json", encoding="utf8") as f:
        cards_list = json.loads(f.read())
    cards = {}
    # print(cards_list[0].keys())
    # print(cards_list[0]["name"])
    for card in cards_list:
        name = card["name"]
        if cards.get(name):
            cards[name].append(card)
        else:
            cards[name] = [card]
    return cards

if time.time() - os.path.getmtime("default-cards.json") > 86400:
    update_data()

cards = init_cards()



def main():
    pass
if __name__=="__main__":
    main()