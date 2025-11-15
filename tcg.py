import pprint

import data
from selenium import webdriver

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import time
import re


class Vendor:
    __lastId = 0

    def __init__(self, name, url, shipping):
        self.name = name
        self.url = url
        self.shipping = shipping
        self.id = Vendor.__lastId
        Vendor.__lastId += 1


class Listing:
    def __init__(self, name, url, price, vendor=None):
        self.name = name
        self.url = url
        self.price = price
        self.vendor = vendor


class State:
    def __init__(self, under_five, card_to_store, shipping_covered=None, price=0):
        if shipping_covered is None:
            shipping_covered = set()
        # shipping_covered = [False] * len(under_five)
        # card_to_store = []
        self.shipping_covered = shipping_covered
        self.under_five = under_five
        self.card_to_store = card_to_store
        self.price = price

    def add_card(self, listing, vendor, price):
        shipping_covered = self.shipping_covered.copy()
        under_five = self.under_five.copy()
        # card_to_store = copy.deepcopy(self.card_to_store)
        card_to_store = self.card_to_store.copy()
        # if shipping_covered[vendor.id]:
        #    pass
        if vendor.id in shipping_covered:
            pass
        else:
            price += 1.3
            under_five[vendor.id] += price
            if under_five[vendor.id] >= 5:
                # shipping_covered[vendor.id] = True
                shipping_covered.add(vendor.id)
                price -= 1.3
        # print(len(card_to_store))
        # card_to_store[vendor.id].append(listing)
        card_to_store.append(listing)

        return State(under_five, card_to_store, shipping_covered, self.price + price)


def url_build(tcd_id):
    url = "https://www.tcgplayer.com/product/{}?".format(tcd_id)
    url += "&Language=English"
    url += "&Condition=Near+Mint|Lightly+Played"
    return url


def read_card(card, vendors, driver):
    prices = []
    for printing in card:
        prices.append(printing["price"])
    price_min, price_max = min(prices), max(prices)
    if price_min > 10:
        price_cutoff = price_min * 1.3 + 1
    else:
        price_cutoff = max(price_min * 1.3, price_min + 0.3)
    index_to_delete = []
    for idx, price in enumerate(prices):
        if price > price_cutoff:
            index_to_delete.append(idx)
    index_to_delete.sort(reverse=True)
    for idx in index_to_delete:
        card.pop(idx)
    if len(card) > 15:
        card = card[:15]
    listings = []

    for printing in card:
        url = url_build(printing["tcgplayer_id"])
        driver.get(url)
        time.sleep(0.5)
        # try:
        #    WebDriverWait(driver, 3).until(
        #        expected_conditions.presence_of_element_located((By.CLASS_NAME, "listing-item"))
        #    )
        # except TimeoutException:
        #    print("Failed to find listings for printing:\n{}".format(printing))
        #    continue
        elements = driver.find_elements(By.CLASS_NAME, "listing-item")

        for element in elements:

            price_element = element.find_element(By.CLASS_NAME, "listing-item__listing-data__info")

            match = re.search(r"Over \$\d+", price_element.text)
            shipping_type = None
            if match:
                shipping_type = int(match.group().split(" ")[1][1:])
            shipping = 0
            match = re.search(r"\$\d+\.\d{2}\sShipping[^:]", price_element.text + " ")
            if match:
                shipping = float(match.group().split(" ")[0][1:])
            price = float(
                price_element.find_element(By.CLASS_NAME, "listing-item__listing-data__info__price").text[1:].replace(
                    ',', ''))
            if not shipping_type:
                price += shipping
                shipping_type = 0
            elif shipping_type == 50:
                continue

            vendor = element.find_element(By.CLASS_NAME, "seller-info__name")
            vendor_name = vendor.text
            vendor_url = vendor.get_attribute("href")
            if vendor_name not in vendors:
                vendors[vendor_name] = Vendor(vendor_name, vendor_url, shipping)
                print("adding new vendor:{}".format(vendor_name))
            # print(vendor_name, vendor_url, price, shipping, shipping_type)
            listing = Listing(printing["name"], url, price, vendors[vendor_name])
            listings.append(listing)

    return listings


def optimize(vendors, card_listings):
    v = set()
    v2 = []
    for vendor in vendors:
        # print(vendors[vendor].id)
        # vendors[vendor].id -= 961
        v.add(vendors[vendor].id)
        v2.append(vendors[vendor].id)
    v2.sort()
    print(v2[0:100])
    print(len(vendors))
    print(len(v))
    # return
    temp = []
    for x in range(len(vendors)):
        temp.append([])
    # print([[] for x in range(len(vendors))])
    options = [State([0] * len(vendors), [])]
    vendor_score = [0] * len(vendors)
    # print(card_listings)
    for card in card_listings:
        for listing in card_listings[card]:
            # print(listing)
            # print(listing.vendor.id)
            vendor_score[listing.vendor.id] += 1
    print(vendor_score)
    vendor_score = [x * 0.02 for x in vendor_score]
    for card in card_listings:
        card_listings[card].sort(key=lambda x: x.price - vendor_score[x.vendor.id])
    w = 0
    card_listings.pop("Dark Ritual")
    card_listings.pop("Timeline Culler")
    for x in card_listings.keys():
        y = card_listings[x]
        print(x)
        print(len(y))
        c = y[0]
        p = c.price
    keys = sorted(card_listings.keys(), key=lambda x: card_listings[x][0].price, reverse=True)
    for card in keys:

        if w == 5:
            pass
            # break
        w += 1
        new_options = []
        start = time.time()
        for option in options:
            cheapest_shipping_covered = False
            under_five = 2
            if w > 50:
                fresh = 1
            else:
                fresh = 2
            for listing in card_listings[card]:
                price = listing.price
                vendor = listing.vendor
                # if price > 5 or option.shipping_covered[vendor.id]:
                if price > 5 or vendor.id in option.shipping_covered:
                    if not cheapest_shipping_covered:
                        new_options.append(option.add_card(listing, vendor, price))
                        cheapest_shipping_covered = True

                elif option.under_five[vendor.id] and under_five:
                    under_five -= 1
                    new_options.append(option.add_card(listing, vendor, price))
                elif fresh:
                    new_options.append(option.add_card(listing, vendor, price))
                    fresh -= 1
                elif not cheapest_shipping_covered and not under_five and not fresh:
                    break
        options = new_options
        end = time.time()
        print("time taken: {} Option size: {}".format(end - start, len(options)))
        if end - start > 0.5:
            options.sort(key=lambda o: o.price)
            options = options[:len(options) // 10]
            # cull
    options.sort(key=lambda o: o.price)
    print(options[0].price)
    print(options[0].card_to_store)
    for listing in options[0].card_to_store:
        print("card: {}, price: {}, vendor: {} ,link {}".format(listing.name, listing.price, listing.vendor.name,
                                                                listing.url, ))
        # pprint.pprint(array)
    return options[0]


def buy(option, driver):
    for listing in option.card_to_store:
        driver.get(listing.url)
        time.sleep(0.5)
        elements = driver.find_elements(By.CLASS_NAME, "listing-item")

        for element in elements:
            price_element = element.find_element(By.CLASS_NAME, "listing-item__listing-data__info")

            match = re.search(r"Over \$\d+", price_element.text)
            shipping_type = None
            if match:
                shipping_type = int(match.group().split(" ")[1][1:])
            if shipping_type == 50:
                continue

            vendor = element.find_element(By.CLASS_NAME, "seller-info__name")
            vendor_name = vendor.text
            if vendor_name == listing.vendor.name:
                add_element = element.find_element(By.CLASS_NAME, "add-to-cart")
                print("found listing")
                button = add_element.find_element(By.TAG_NAME, "button")
                header = driver.find_element(By.CLASS_NAME, "horizontal-filters-bar")
                driver.execute_script("""var element = arguments[0];element.parentNode.removeChild(element); """,
                                      header)
                driver.execute_script("arguments[0].scrollIntoView();", button)
                # time.sleep(1)
                ActionChains(driver).scroll_to_element(button).perform()
                print(button.text)
                print(button.get_attribute('innerHTML'))
                print(button)

                # return

                button.click()
                driver.find_element(By.CLASS_NAME, "tcg-snackbar__message")
                # return

                break


def main():
    # Get card processed card data from scryfall
    card_data = data.init_cards()
    with open("a_deck.txt", encoding="utf8") as f:
        lines = f.readlines()
    card_names = []
    # strip amounts of cards, We assumed only 1 of each card
    for line in lines:
        card_names.append(line[1:].strip())
    cards = {}
    for card_name in card_names:
        try:
            cards[card_name] = card_data[card_name]
        except KeyError as e:
            pprint.pprint(e)
            print("failed to find card" + card_name)
            exit(1)

    card_listings = {}
    vendors = {}  # dict containing TCG vendors

    # driver init
    driver = webdriver.Firefox()
    driver.implicitly_wait(3)
    url = url_build(196523)
    driver.get(url)
    time.sleep(2)
    driver.find_elements(By.CLASS_NAME, "tcg-input-select__trigger-container")[1].click()
    time.sleep(1)
    drop_downs = driver.find_elements(By.CLASS_NAME, "tcg-base-dropdown__item-content")
    for drop_down in drop_downs:
        if drop_down.text == "50":
            drop_down.click()
    for card in cards:
        card_listings[card] = read_card(cards[card], vendors, driver)

    option = optimize(vendors, card_listings)
    buy(option, driver)


if __name__ == "__main__":
    main()
