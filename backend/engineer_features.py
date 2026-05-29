import pandas as pd
import numpy as np

# Load original dataset
df = pd.read_csv('dataset.csv')

# Drop NA rows temporarily to calculate bounds or fill them
df = df.ffill().bfill()

# --- INPUTS ---
np.random.seed(42)
# Tax Rate (0-60% UI). Typically statutory rates are higher than revenue % GDP.
df['Tax_Rate'] = df['Tax_Revenue_Pct_GDP'] * 1.5 + np.random.uniform(0, 5, len(df))

# Fuel Price (1-10$ UI)
# Higher CO2 implies higher demand/production, inflation adds to price.
co2_norm = (df['CO2_Emissions'] - df['CO2_Emissions'].min()) / (df['CO2_Emissions'].max() - df['CO2_Emissions'].min())
df['Fuel_Price'] = 1.5 + co2_norm * 3.5 + (df['Inflation_CPI'] / 10.0) + np.random.uniform(-0.5, 0.5, len(df))
df['Fuel_Price'] = df['Fuel_Price'].clip(lower=1.0)

# Public Spending (10-60% UI)
# Public spending is usually Tax Revenue + Deficit (2-10%)
df['Public_Spending'] = df['Tax_Revenue_Pct_GDP'] + np.random.uniform(2, 15, len(df))

# Subsidy Level (0-50% UI)
# Subsidy as a % of GDP or % of Spending. Let's make it 10-30% of public spending.
df['Subsidy_Level'] = df['Public_Spending'] * np.random.uniform(0.1, 0.4, len(df))

# Interest Rate (0-20% UI)
# Correlates with inflation (Taylor Rule proxy)
df['Interest_Rate'] = df['Inflation_CPI'] * 0.8 + np.random.uniform(0, 4, len(df))
df['Interest_Rate'] = df['Interest_Rate'].clip(lower=0)

# Environmental Regulation (0-100 UI)
# Historically low when CO2 was growing fast, high now. Inverse to CO2 norm roughly, but let's just make it grow over time.
# We'll use Year as a proxy for growing regulation.
year_norm = (df['Year'] - df['Year'].min()) / (df['Year'].max() - df['Year'].min())
df['Environmental_Regulation'] = year_norm * 80 + np.random.uniform(0, 20, len(df))


# --- OUTPUTS ---
# Employment Rate
df['Employment_Rate'] = 100 - df['Unemployment_Pct']

# Environment Score (/100)
df['Environment_Score'] = df['Environmental_Regulation'] * 0.6 + (1 - co2_norm) * 40 + np.random.uniform(-5, 5, len(df))
df['Environment_Score'] = df['Environment_Score'].clip(0, 100)

# Public Satisfaction (%)
# Composite: GDP growth (good), Employment (good), Inflation (bad)
base_sat = 50 + (df['GDP_Growth'] * 3) + (df['Employment_Rate'] - 90) * 2 - (df['Inflation_CPI'] * 2)
df['Public_Satisfaction'] = base_sat + np.random.uniform(-5, 5, len(df))
df['Public_Satisfaction'] = df['Public_Satisfaction'].clip(0, 100)

df.to_csv('augmented_dataset.csv', index=False)
print("Successfully created augmented_dataset.csv with all required features.")
