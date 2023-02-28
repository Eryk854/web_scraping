import pandas as pd

# initial preparation of otodom data
file_path = "otodom/otodom.csv"
df = pd.read_csv(file_path, sep="\t")
df = df[(~df["Cena"].isin(["1 000 000 USD", "1 000 000 EUR"])) & (df["Cena"] != "Zapytaj o cene")]
df.to_csv("otodom/otodom_initial_preprocess.csv", index=False, sep="\t")

# initial preparation of nieruchomosci-online data
file_path = "nieruchomosci/nieruchomosci_online.csv"
df = pd.read_csv(file_path, sep="\t")
types_of_advert = [
    "mieszkanie na sprzedaz",
    "nowe mieszkanie na sprzedaz",
    "kawalerka na sprzedaz"
]
df = df.loc[
    (df["Typ oferty:"].isin(types_of_advert)) &
    (df["Cena"] != "Zapytaj o cene") &
    (~df["Cena"].str.contains("EUR")) &
    (~df["Cena"].str.contains("\$"))
]
df = df.loc[:, ~df.isna().all()]

df.loc[(df[" okna"].isna()), " okna"] = ""
df.loc[(df["okna"].isna()), "okna"] = ""
df["okna"] = df[" okna"] + df["okna"]
df = df.drop(columns=["Mozliwa zamiana:", "Stan inwestycji:", "Mozliwe przeznaczenie:", "Cena:", "Rozklad mieszkania:", "  ", " okna"])
df = df.rename(columns={" ": "winda"})
new_columns_names = [column_name.replace(":", "") for column_name in df.columns]
df.columns = new_columns_names
df.to_csv("nieruchomosci/nieruchomosci_online_initial_preprocess.csv", index=False, sep="\t")
