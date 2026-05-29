import requests
import pandas as pd
from functools import reduce

urls = {
    "GDP_Growth": "https://api.worldbank.org/v2/country/IND/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=60",
    "Inflation_CPI": "https://api.worldbank.org/v2/country/IND/indicator/FP.CPI.TOTL.ZG?format=json&per_page=60",
    "Tax_Revenue_Pct_GDP": "https://api.worldbank.org/v2/country/IND/indicator/GC.TAX.TOTL.GD.ZS?format=json&per_page=60",
    "Unemployment_Pct": "https://api.worldbank.org/v2/country/IND/indicator/SL.UEM.TOTL.ZS?format=json&per_page=60",
    "CO2_Emissions": "https://api.worldbank.org/v2/country/IND/indicator/EN.GHG.CO2.MT.CE.AR5?format=json&per_page=60",
    "FDI_Net_Inflows_Pct_GDP": "https://api.worldbank.org/v2/country/IND/indicator/BX.KLT.DINV.WD.GD.ZS?format=json&per_page=60"
}

def fetch_data(url):
    print(f"Fetching data from {url}")
    response = requests.get(url)
    data = response.json()
    if len(data) > 1:
        records = data[1]
        # extract year and value
        parsed = [{"Year": int(r["date"]), "Value": r["value"]} for r in records]
        return pd.DataFrame(parsed)
    return pd.DataFrame()

dfs = []
for name, url in urls.items():
    df = fetch_data(url)
    if not df.empty:
        df.rename(columns={"Value": name}, inplace=True)
        dfs.append(df)

if dfs:
    # Merge all DataFrames on Year
    merged_df = reduce(lambda left, right: pd.merge(left, right, on="Year", how="outer"), dfs)
    merged_df.sort_values("Year", ascending=False, inplace=True)
    merged_df.to_csv("dataset.csv", index=False)
    print("Data fetched, merged, and saved to dataset.csv")
    print(merged_df.head())
else:
    print("No data fetched.")
