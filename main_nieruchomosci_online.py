from typing import List, Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from unidecode import unidecode


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    # options.add_argument('--headless')

    driver = webdriver.Chrome(chrome_options=options)

    # take number of listing pages regarding specified city (first listing page)
    city = "Gdansk"
    listing_page_url = "https://gdansk.nieruchomosci-online.pl"
    file_name = "nieruchomosci/nieruchomosci_online_gdansk1.csv"

    driver.get(listing_page_url)
    source_code = driver.page_source
    bs = BeautifulSoup(source_code, "html.parser")

    pagination_wrapper = bs.find("div", attrs={"id": "pagination-outer"})
    pagination_list = pagination_wrapper.find("ul", attrs={"class": "pagination-mob-sub"})
    pagination_list_element = pagination_list.contents[-2]
    list_site_max_number = int(pagination_list_element.text)

    # Take ad urls from the listing page
    paths = []
    for i in range(1, 10):
        driver.get(f"{listing_page_url}/?p={i}")
        source_code = driver.page_source
        bs = BeautifulSoup(source_code, "html.parser")

        main_list_div = bs.find("div", attrs={"id": "main-sub"})
        div_with_adds = main_list_div.find("div", attrs={"class": "column-container column_default"})
        for add_div in div_with_adds.contents:
            if add_div.name == "div":
                a_tag = add_div.find("a")
                if a_tag:
                    a_href = a_tag.attrs["href"]
                    paths.append(a_href)

    # paths = [
    #     "https://borkowo.nieruchomosci-online.pl/nowy-dom,osiedle-zielony-zakatek-ii/23527745.html",
    #     "https://warszawa.nieruchomosci-online.pl/lokal-uzytkowy,na-sprzedaz/23880094.html"
    # ]
    result_list = []
    for path in paths:
        driver.get(path)

        source_code = driver.page_source
        bs = BeautifulSoup(source_code, "html.parser")

        # Take the most important information about advertisement like price and area
        print(path)
        price_main_div = bs.find("div", attrs={"id": "bottomBox"})
        if price_main_div:
            primary_price_element = price_main_div.find("p", attrs={"class": "info-primary-price"})
            area_element = price_main_div.find("p", attrs={"class": "info-area"})
            secondary_price_element = price_main_div.find("p", attrs={"class": "info-secondary-price"})
            title_element = price_main_div.find("h1")

            # Check if ad contain price. Some advertisements don't contain price because they require
            # contact with the saler
            if primary_price_element and secondary_price_element:
                primary_price = unidecode(primary_price_element.text)
                secondary_price = unidecode(secondary_price_element.text)
            else:
                # Price not included in the advertisement
                primary_price = "Zapytaj o cene"
                secondary_price = "Zapytaj o cene"
            area = unidecode(area_element.text)
            title = unidecode(title_element.text)

            # take full advertisement address
            address_div = bs.find("div", attrs={"id": "locationTable"})
            list_element_with_address = address_div.find("li", attrs={"class": "adress"})
            if list_element_with_address:
                span_address = list_element_with_address.find("span")
                address = unidecode(span_address.text)
            else:
                list_elements = address_div.find_all("li")
                for list_element in list_elements:
                    element_text = list_element.text
                    split_text = element_text.split(":")
                    if len(split_text) == 2 and split_text[0] == "Adres":
                        address = unidecode(split_text[1])
            res = {
                "Miasto": city,
                "URL": path,
                "Cena": primary_price,
                "Powierzchnia": area,
                "Cena za metr": secondary_price,
                "Tytul": title,
                "Adres": address
            }

            # take information under the photo, like floor and year of construction
            main_offer_div = bs.find("div", attrs={"class": "box-offer-inside mod-a mobile"})
            main_info_div = main_offer_div.find("div", attrs={"class": "table-d__changer"})
            main_info_divs = main_info_div.contents
            for info_div in main_info_divs:
                # iterate over every element with main information (under photo)
                if info_div.name == "div":
                    info = info_div.contents[1]
                    title_element = info.find("p")
                    value_elements = info.find_all("span")

                    title = title_element.text
                    title = unidecode(title)

                    # value of main info can contain multiple span elements e.g. floor 3/3.
                    # Need to iterate over all elements to create value string
                    value = ""
                    for value_element in value_elements:
                        value += value_element.text
                    value = unidecode(value)

                    res[title] = value

            # take additional information from "Szczegóły ogłoszenia" section
            details_main_div = bs.find("div", attrs={"id": "detailsTable"})
            detail_elements = details_main_div.find_all("li")

            # iterate over all additional information elements
            for detail_element in detail_elements:
                detail_title = detail_element.find("strong")
                detail_value = detail_element.find("span")

                if detail_title.text == " " and len(detail_value.text.split(":")) > 1:
                    # detail information may not have title but still contain useful information
                    # example format technika budowy: tradycyjna/cegła; okna: plastikowe
                    # It would be helpful to have technika budowy and okna variables in the dataframe
                    multiple_infor = detail_value.text.split(";")  # first we split info by semicolon sign
                    for single_inf in multiple_infor:
                        # Iterate over elements separated by semicolon
                        split_list = single_inf.split(":")  # split wanted title -> values pairs
                        if len(split_list) == 2:
                            detail_title = unidecode(split_list[0])
                            detail_value = unidecode(split_list[1])
                        else:
                            detail_title = unidecode(split_list[0])
                            detail_value = unidecode("")
                        res[detail_title] = detail_value
                else:
                    # detail information are good formatted and contain span and strong elements
                    detail_title = unidecode(detail_title.text)
                    detail_value = unidecode(detail_value.text)
                    res[detail_title] = detail_value

            result_list.append(res)
        else:
            print(path)

    df = pd.DataFrame(result_list)
    df.replace(";", ",", inplace=True, regex=True)
    df.to_csv(file_name, index=False, sep="\t")
