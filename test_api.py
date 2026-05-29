import requests

data = {
    'Inflation_CPI': 5,
    'Tax_Revenue_Pct_GDP': 15,
    'Unemployment_Pct': 7,
    'CO2_Emissions': 2500000,
    'FDI_Net_Inflows_Pct_GDP': 2,
    'Interest_Rate': 5,
    'Fuel_Price': 100,
    'Subsidy_Level': 2,
    'Public_Spending': 30,
    'Environmental_Regulation': 50
}

response = requests.post('http://localhost:8000/predict', json=data)
print("Status Code:", response.status_code)
print("Response:", response.json())
