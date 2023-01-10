from typing import List, Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from unidecode import unidecode


# def get_price_tag_based_on_title_tag(title_tag: str) -> Tag:
#     title_tag_siblings = list(title_tag.next_siblings)
#     for title_sibling in title_tag_siblings:
#         if title_sibling.attrs.get("aria-label") == "Cena":
#             return title_sibling
#
#
# def get_paths_from_listening_page(adds_list_url: str) -> List[str]:
#     driver.get(adds_list_url)
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#
#     page_source = driver.page_source
#     bs = BeautifulSoup(page_source, "html.parser")
#
#     search_div = bs.find_all("div", attrs={"data-cy": "search.listing"})
#     if not search_div:
#         driver.refresh()
#         page_source = driver.page_source
#         bs = BeautifulSoup(page_source, "html.parser")
#         search_div = bs.find_all("div", attrs={"data-cy": "search.listing"})
#
#     paths = []
#     if search_div:
#         li_elements = search_div[1].findChildren("li")
#         for li_element in li_elements:
#             a_tag = li_element.findChildren("a")
#             if a_tag:
#                 href = a_tag[0].attrs["href"]
#                 paths.append(href)
#     return paths
#
#
# def get_title_and_price(bs) -> Tuple[Optional[str], Optional[str]]:
#     house_title_tag = bs.find("h1", attrs={"data-cy": "adPageAdTitle"})
#     if not house_title_tag:
#         driver.refresh()
#         page_source = driver.page_source
#         bs = BeautifulSoup(page_source, "html.parser")
#         house_title_tag = bs.find("h1", attrs={"data-cy": "adPageAdTitle"})
#
#     if house_title_tag:
#         price_tag = get_price_tag_based_on_title_tag(house_title_tag)
#
#         house_title = house_title_tag.contents[0]
#         price_value = price_tag.contents[0]
#         house_title = unidecode(house_title)
#         price_value = unidecode(price_value)
#         return house_title, price_value
#     return None, None
#
#
# def get_main_information(bs):
#     main_data_div = bs.find("div", attrs={"data-testid": "ad.top-information.table"})
#
#     if not main_data_div:
#         driver.refresh()
#         page_source = driver.page_source
#         bs = BeautifulSoup(page_source, "html.parser")
#         main_data_div = bs.find("div", attrs={"data-testid": "ad.top-information.table"})
#
#     data_divs = main_data_div.findChild("div")
#     for data_div in data_divs:
#         _, data_name_div, data_value_div = data_div.contents
#         data_name = data_name_div.string
#         data_name = unidecode(data_name)
#
#         if len(data_value_div.contents) != 1:
#             data_value_div = data_value_div.find("div")
#
#         value = data_value_div.string
#
#         if not value:
#             value = data_value_div.contents[0].contents[0].string
#
#         value = unidecode(value)
#         res[data_name].append(value)
#
#
# def get_additional_information(bs):
#     additional_information_main_div = bs.find("div", attrs={"data-testid": "ad.additional-information.table"})
#
#     if additional_information_main_div:
#         additional_information_divs = additional_information_main_div.contents[1]
#
#         for additional_information_div in additional_information_divs.contents:
#             additional_title_div, additional_value_div = additional_information_div.contents
#             additional_title = additional_title_div.string
#             additional_title = unidecode(additional_title)
#
#             additional_value = additional_value_div.string
#             additional_value = unidecode(additional_value)
#
#             res[additional_title].append(additional_value)
#     else:
#         res["Rynek"].append(None)
#         res["Typ ogloszeniodawcy"].append(None)
#         res["Dostepne od"].append(None)
#         res["Rok budowy"].append(None)
#         res["Rodzaj zabudowy"].append(None)
#         res["Okna"].append(None)
#         res["Winda"].append(None)
#         res["Media"].append(None)
#         res["Zabezpieczenia"].append(None)
#         res["Wyposazenie"].append(None)
#         res["Informacje dodatkowe"].append(None)
#         res["Material budynku"].append(None)


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

    paths = [
        "https://warszawa.nieruchomosci-online.pl/mieszkanie-w-apartamentowcu,wysoki-standard/23877359.html",
        "https://warszawa.nieruchomosci-online.pl/mieszkanie,z-aneksem-kuchennym/23787685.html"

    ]
    result_list = []
    for path in paths:
        driver.get(path)

        source_code = driver.page_source
        bs = BeautifulSoup(source_code, "html.parser")

        price_main_div = bs.find("div", attrs={"id": "bottomBox"})
        primary_price_element = price_main_div.find("p", attrs={"class": "info-primary-price"})
        area_element = price_main_div.find("p", attrs={"class": "info-area"})
        secondary_price_element = price_main_div.find("p", attrs={"class": "info-secondary-price"})
        address_element = price_main_div.find("h1")

        primary_price = unidecode(primary_price_element.text)
        area = unidecode(area_element.text)
        secondary_price = unidecode(secondary_price_element.text)
        address = unidecode(address_element.text)

        res = {
            "Cena": primary_price,
            "Powierzchnia": area,
            "Cena za metr": secondary_price,
            "Adres": address,
        }
        # res["Cena"].append(primary_price)
        # res["Powierzchnia"].append(area)
        # res["Cena za metr"].append(secondary_price)
        # res["Adres"].append(address)

        main_offer_div = bs.find("div", attrs={"class": "box-offer-inside mod-a mobile"})
        main_info_div = main_offer_div.find("div", attrs={"class": "table-d__changer"})
        main_info_divs = main_info_div.contents
        for info_div in main_info_divs:
            if info_div.name == "div":
                info = info_div.contents[1]
                title_element = info.find("p")
                value_elements = info.find_all("span")

                title = title_element.text
                title = unidecode(title)

                value = ""
                for value_element in value_elements:
                    value += value_element.text
                value = unidecode(value)

                res[title] = value

                # if title not in res.keys():
                #     res[title] = [value]
                # else:
                #     res[title].append(value)

        details_main_div = bs.find("div", attrs={"id": "detailsTable"})
        detail_elements = details_main_div.find_all("li")
        for detail_element in detail_elements:
            detail_title, _, detail_value = detail_element.contents
            detail_title = unidecode(detail_title.text)
            detail_value = unidecode(detail_value.text)

            if "numer ogloszenia" not in detail_value:
                res[detail_title] = detail_value

            if "technika budowy: " in detail_value:
                res["technika budowy"] = detail_value.lstrip("technika budowy: ")

            # if detail_title not in res.keys():
            #     res[detail_title] = [detail_value]

        print(res)
        result_list.append(res)

    df = pd.DataFrame(result_list)
    df.replace(";", ",", inplace=True, regex=True)
    df.to_csv("nieruchomosci_online.csv", index=False, sep="\t")
