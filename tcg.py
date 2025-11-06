
"""
card: scryfall object containing all the information on a given card
tcg_price: information for the price of  card from a vendor
            dict{ card_name: str
                vendor_name: str
                price: float
                card_url: str
                vendor_url: str
                shipping_type: str
                }
tcg_vendor: contains list of possible cards we may want to purchase from a vendor
            dict{ cards: [tcg_price]
            vendor_name: str
            vendor_url: str
            shipping_type: str
            }
"""

"""
Basic algorith

get data from scryfall
get cards we want to purchase form csv

filter card printing we consider

search tcg for card prices of printings we want to consider

calculate best sale option

select cards to purchase

pass it off to a human to finilaize purchase
"""


def read_card(card, tcg_params):
    """

    :param tcg_params:
    :param card:
    :return list:
    """
    return []


def url_build():
    pass


def main():
    pass
if __name__=="__main__":
    main()