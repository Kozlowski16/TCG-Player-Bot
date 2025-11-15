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


def init_cards(images = False):
    if time.time() - os.path.getmtime("default-cards.json") > 86400:
        print("Updating default-cards.json")
        update_data()

    with open("default-cards.json", encoding="utf8") as f:
        scryfall_data = json.load(f)
    cards = {}
    #TODO get tournament illegal card sets from scryfall instead of hard codding them in
    banned_sets = ("cei", "wc04")
    for card in scryfall_data:
        if card["set"] in banned_sets:
            continue
        if "tcgplayer_id" not in card:
            continue
        prices = []
        for currency in ["usd", "usd_foil", "usd_etched"]:
            if card["prices"][currency]:
                prices.append(float(card["prices"][currency]))
        if not prices:
            continue

        processed_card = {"price": min(prices)}
        properties = ["id", "tcgplayer_id", "name", "image_uris"]
        # handle dual-sided card edge case
        if images:
            if "card_faces" in card and "image_uris" not in card:
                processed_card["image_uris"] = [card["card_faces"][0]["image_uris"], card["card_faces"][1]["image_uris"]]
                properties.remove("image_uris")
        else:
            properties.remove("image_uris")

        for key in properties:
            if key in card:
                processed_card[key] = card[key]
            else:
                print("Error: Failed to find key: {}".format(key))
                pprint.pprint(card)
                exit(1)
        name = card["name"]
        if name in cards:
            cards[name].append(processed_card)
        else:
            cards[name] = [processed_card]

    for printing_list in cards:
        cards[printing_list].sort(key=lambda x: x["price"])

    return cards

def main():
    cards = init_cards()
    pprint.pprint(cards["Sol Ring"])

if __name__ == "__main__":
    main()