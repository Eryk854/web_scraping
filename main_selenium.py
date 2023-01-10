from typing import List, Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from unidecode import unidecode


def get_price_tag_based_on_title_tag(title_tag: str) -> Tag:
    title_tag_siblings = list(title_tag.next_siblings)
    for title_sibling in title_tag_siblings:
        if title_sibling.attrs.get("aria-label") == "Cena":
            return title_sibling


def get_paths_from_listening_page(adds_list_url: str) -> List[str]:
    driver.get(adds_list_url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    page_source = driver.page_source
    bs = BeautifulSoup(page_source, "html.parser")

    search_div = bs.find_all("div", attrs={"data-cy": "search.listing"})
    if not search_div:
        driver.refresh()
        page_source = driver.page_source
        bs = BeautifulSoup(page_source, "html.parser")
        search_div = bs.find_all("div", attrs={"data-cy": "search.listing"})

    paths = []
    if search_div:
        li_elements = search_div[1].findChildren("li")
        for li_element in li_elements:
            a_tag = li_element.findChildren("a")
            if a_tag:
                href = a_tag[0].attrs["href"]
                paths.append(href)
    return paths


def get_title_and_price(bs) -> Tuple[Optional[str], Optional[str]]:
    house_title_tag = bs.find("h1", attrs={"data-cy": "adPageAdTitle"})
    if not house_title_tag:
        driver.refresh()
        page_source = driver.page_source
        bs = BeautifulSoup(page_source, "html.parser")
        house_title_tag = bs.find("h1", attrs={"data-cy": "adPageAdTitle"})

    if house_title_tag:
        price_tag = get_price_tag_based_on_title_tag(house_title_tag)

        house_title = house_title_tag.contents[0]
        price_value = price_tag.contents[0]
        house_title = unidecode(house_title)
        price_value = unidecode(price_value)
        return house_title, price_value
    return None, None


def get_main_information(bs):
    main_data_div = bs.find("div", attrs={"data-testid": "ad.top-information.table"})

    if not main_data_div:
        driver.refresh()
        page_source = driver.page_source
        bs = BeautifulSoup(page_source, "html.parser")
        main_data_div = bs.find("div", attrs={"data-testid": "ad.top-information.table"})

    data_divs = main_data_div.findChild("div")
    for data_div in data_divs:
        _, data_name_div, data_value_div = data_div.contents
        data_name = data_name_div.string
        data_name = unidecode(data_name)

        if len(data_value_div.contents) != 1:
            data_value_div = data_value_div.find("div")

        value = data_value_div.string

        if not value:
            value = data_value_div.contents[0].contents[0].string

        value = unidecode(value)
        res[data_name].append(value)


def get_additional_information(bs):
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


def get_detail_info(detail_site_url: str):
    driver.get(detail_site_url)
    page_source = driver.page_source
    bs = BeautifulSoup(page_source, "html.parser")
    res["Url"].append(detail_site_url)

    house_title, price_value = get_title_and_price(bs)

    if house_title:
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

    all_paths = []
    for i in range(1, 10):
        url = f"https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?page={i}"
        listed_paths = get_paths_from_listening_page(adds_list_url=url)
        all_paths.extend(listed_paths)

    main_url = "https://www.otodom.pl"

    res = {
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
    df.to_csv("test.csv", index=False)
