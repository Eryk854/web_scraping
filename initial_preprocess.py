import pandas as pd

# initial preparation of otodom data
file_path = "otodom/otodom.csv"
df = pd.read_csv(file_path, sep="\t")
df = df[(~df["Cena"].isin(["1 000 000 USD", "1 000 000 EUR"])) & (df["Cena"] != "Zapytaj o cene")]
df.to_csv("otodom/otodom_with_price.csv", index=False, sep="\t")

# initial preparation of nieruchomosci-online data
file_path = "nieruchomosci/nieruchomosci_online.csv"
df = pd.read_csv(file_path, sep="\t")
types_of_advert = [
    "mieszkanie na sprzedaz",
    "maly dom na sprzedaz",
    "nowe mieszkanie na sprzedaz",
    "nowy dom na sprzedaz",
    "dom na sprzedaz",
    "kawalerka na sprzedaz"
]
df = df.loc[(df["Typ oferty:"].isin(types_of_advert)) & (df["Cena"] != "Zapytaj o cene")]
df.to_csv("nieruchomosci/nieruchomosci_online_with_price.csv", index=False, sep="\t")
