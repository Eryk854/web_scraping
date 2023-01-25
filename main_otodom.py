from typing import List, Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from unidecode import unidecode


def get_paths_from_listening_page(ads_list_url: str) -> List[str]:
    """Get all url to detail ad information from the listening page"""
    driver.get(ads_list_url)
    # needs to scroll page down to get all site content
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    page_source = driver.page_source
    bs = BeautifulSoup(page_source, "html.parser")

    search_div = bs.find("div", attrs={"data-cy": "search.listing.organic"})
    # check if page was loaded successfully. Sometime otodom return a dummy page with error
    if not search_div:
        # if the invalid page was returned, reload the site
        driver.refresh()
        page_source = driver.page_source
        bs = BeautifulSoup(page_source, "html.parser")
        search_div = bs.find("div", attrs={"data-cy": "search.listing.organic"})

    # take all urls from the listing site based on a tag in HTML li
    paths = []
    if search_div:
        li_elements = search_div.findChildren("li")
        for li_element in li_elements:
            a_tag = li_element.findChildren("a")
            if a_tag:
                href = a_tag[0].attrs["href"]
                paths.append(href)
    return paths


def get_price_tag_based_on_title_tag(title_tag: str) -> Tag:
    """Helper function which gets the HTML tag with the price value"""
    title_tag_siblings = list(title_tag.next_siblings)
    for title_sibling in title_tag_siblings:
        if title_sibling.attrs.get("aria-label") == "Cena":
            return title_sibling


def get_address_tag_based_on_title_tag(title_tag: Tag) -> Tag:
    """Helper function which gets the HTML tag with the price value"""
    address_tag = title_tag.find("a", {"aria-label": "Adres"})
    if not address_tag:
        address_tag = None
    return address_tag


def get_title_and_price(bs: BeautifulSoup) -> Tuple[Optional[str], Optional[str]]:
    """Get title and price information from the detail site"""
    house_title_tag = bs.find("h1", attrs={"data-cy": "adPageAdTitle"})

    # check if page was loaded successfully. Sometime otodom return a dummy page with error
    if not house_title_tag:
        # if the invalid page was returned, reload the site
        driver.refresh()
        page_source = driver.page_source
        bs = BeautifulSoup(page_source, "html.parser")
        house_title_tag = bs.find("h1", attrs={"data-cy": "adPageAdTitle"})

    if house_title_tag:
        # extract the price and house title value from the website
        price_tag = get_price_tag_based_on_title_tag(house_title_tag)
        address_tag = get_address_tag_based_on_title_tag(house_title_tag.parent)

        house_title = house_title_tag.contents[0]
        price_value = price_tag.contents[0]

        house_title = unidecode(house_title)
        price_value = unidecode(price_value)
        address_value = unidecode(address_tag.text)
        return house_title, price_value, address_value

    # If website don't contain price and house title return None in order to correctly create final dictionary
    return None, None


def get_main_information(bs: BeautifulSoup) -> None:
    """Get main information about the ad. Information from the 'Szczegoly ogloszenia' section """
    main_data_div = bs.find("div", attrs={"data-testid": "ad.top-information.table"})

    # check if page was loaded successfully. Sometime otodom return a dummy page with error
    if not main_data_div:
        # if the invalid page was returned, reload the site
        driver.refresh()
        page_source = driver.page_source
        bs = BeautifulSoup(page_source, "html.parser")
        main_data_div = bs.find("div", attrs={"data-testid": "ad.top-information.table"})

    # every information is under the separate div element. Need to iterate over it to extract all info
    data_divs = main_data_div.findChild("div")
    for data_div in data_divs:
        _, data_name_div, data_value_div = data_div.contents
        data_name = data_name_div.string
        data_name = unidecode(data_name)

        if len(data_value_div.contents) != 1:
            # For some information there is a div under div which contains desired value
            data_value_div = data_value_div.find("div")

        value = data_value_div.string

        if not value:
            # For some information there is more complicated website structure to get desired value
            value = data_value_div.contents[0].contents[0].string

        value = unidecode(value)
        res[data_name].append(value)


def get_additional_information(bs: BeautifulSoup) -> None:
    """Get additional information from the 'Informacje dodatkowe' section"""
    additional_information_main_div = bs.find("div", attrs={"data-testid": "ad.additional-information.table"})

    if additional_information_main_div:
        additional_information_divs = additional_information_main_div.contents[1]

        for additional_information_div in additional_information_divs.contents:
            additional_title_div, additional_value_div = additional_information_div.contents
            additional_title = additional_title_div.string
            additional_title = unidecode(additional_title)

            additional_value = additional_value_div.string
            additional_value = unidecode(additional_value)

            res[additional_title].append(additional_value)
    else:
        res["Rynek"].append(None)
        res["Typ ogloszeniodawcy"].append(None)
        res["Dostepne od"].append(None)
        res["Rok budowy"].append(None)
        res["Rodzaj zabudowy"].append(None)
        res["Okna"].append(None)
        res["Winda"].append(None)
        res["Media"].append(None)
        res["Zabezpieczenia"].append(None)
        res["Wyposazenie"].append(None)
        res["Informacje dodatkowe"].append(None)
        res["Material budynku"].append(None)


def get_detail_info(detail_site_url: str) -> None:
    """Function responsible for extracting all detail information about the add from the website"""
    driver.get(detail_site_url)
    page_source = driver.page_source
    bs = BeautifulSoup(page_source, "html.parser")

    try:
        house_title, price_value, address_value = get_title_and_price(bs)
    except:
        print(detail_site_url)
        house_title = None

    if house_title:
        res["Url"].append(detail_site_url)
        res["Miasto"].append(city_col)
        res["Adres"].append(address_value)
        res["Tytul"].append(house_title)
        res["Cena"].append(price_value)

        get_main_information(bs)
        get_additional_information(bs)
    else:
        print(path)


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    # options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=options)

    # take number of listing pages regarding specified city (first listing page)
    listing_url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa"
    file_name = "otodom/otodom_warszawa7.csv"
    city_col = "warszawa"
    driver.get(listing_url)
    source_code = driver.page_source

    bs = BeautifulSoup(source_code, "html.parser")
    pagination_list = bs.find("nav", attrs={"data-cy": "pagination"})
    pagination_list_element = pagination_list.contents[-2]
    list_site_max_number = int(pagination_list_element.text)

    # Take ad urls from the listing page
    all_paths = []
    for i in range(450, 517):
        url = f"{listing_url}?page={i}"
        listed_paths = get_paths_from_listening_page(ads_list_url=url)
        all_paths.extend(listed_paths)

    # Get detail information about each ad
    main_url = "https://www.otodom.pl"
    res = {
        "Miasto": [],
        "Adres": [],
        "Tytul": [],
        "Url": [],
        "Cena": [],
        "Powierzchnia": [],
        "Liczba pokoi": [],
        "Pietro": [],
        "Czynsz": [],
        "Obsluga zdalna": [],
        "Forma wlasnosci": [],
        "Stan wykonczenia": [],
        "Balkon / ogrod / taras": [],
        "Miejsce parkingowe": [],
        "Ogrzewanie": [],
        "Rynek": [],
        "Typ ogloszeniodawcy": [],
        "Dostepne od": [],
        "Rok budowy": [],
        "Rodzaj zabudowy": [],
        "Okna": [],
        "Winda": [],
        "Media": [],
        "Zabezpieczenia": [],
        "Wyposazenie": [],
        "Informacje dodatkowe": [],
        "Material budynku": [],
    }

    for path in all_paths:
        detail_url = main_url + path
        get_detail_info(detail_url)

    df = pd.DataFrame(res)
    df.to_csv(file_name, index=False, sep="\t")
