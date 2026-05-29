import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import shap
import joblib
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('dataset.csv')

# Drop rows where GDP_Growth is NaN
df = df.dropna(subset=['GDP_Growth']).copy()

# Sort by year to properly create lags and forward fill time-series data
df = df.sort_values(by='Year').reset_index(drop=True)

# For other NaN columns, use forward-fill then backward-fill
df = df.ffill().bfill()

# Features that we want to lag
base_features = ['Inflation_CPI', 'Tax_Revenue_Pct_GDP', 'Unemployment_Pct', 'CO2_Emissions', 'FDI_Net_Inflows_Pct_GDP']

# Feature Engineering: Add Lag Features (1 year and 2 year lags)
lag_features = []
for feature in base_features:
    # Lag 1
    df[f'{feature}_lag1'] = df[feature].shift(1)
    lag_features.append(f'{feature}_lag1')
    # Lag 2
    df[f'{feature}_lag2'] = df[feature].shift(2)
    lag_features.append(f'{feature}_lag2')

# Also add lag of the target variable
df['GDP_Growth_lag1'] = df['GDP_Growth'].shift(1)
lag_features.append('GDP_Growth_lag1')

# Drop the rows that now have NaNs due to shifting (the first 2 years)
df = df.dropna().reset_index(drop=True)

# Combine base features and lag features
all_features = base_features + lag_features

X = df[all_features]
y = df['GDP_Growth']

# Since it's time series, we shouldn't randomly split if we want a realistic evaluation, 
# but sticking to the 80/20 train/test split requested originally (chronological split)
split_idx = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

# Define Hyperparameter Grid for Tuning
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 5, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2', 1.0]
}

# We use TimeSeriesSplit for cross-validation to respect temporal order
tscv = TimeSeriesSplit(n_splits=3)

rf = RandomForestRegressor(random_state=42)
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=tscv, scoring='neg_mean_absolute_error', n_jobs=-1, verbose=1)

print("Starting Hyperparameter Tuning...")
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_
print(f"\nBest Parameters Found: {grid_search.best_params_}")

# Evaluate the best model
y_pred = best_model.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print(f"\nTuned Model Evaluation:")
print(f"R² Score: {r2:.4f}")
print(f"Mean Absolute Error (MAE): {mae:.4f}")

# Save the trained model
joblib.dump(best_model, 'model_tuned.pkl')
print("Model saved to model_tuned.pkl")

# SHAP Explainability
explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_test)

# Calculate mean absolute SHAP value for each feature
mean_abs_shap = np.abs(shap_values).mean(axis=0)
shap_importance = pd.DataFrame(list(zip(all_features, mean_abs_shap)), columns=['Feature', 'SHAP Importance'])
shap_importance = shap_importance.sort_values(by='SHAP Importance', ascending=False).head(10) # Show top 10

print("\nTop 10 SHAP Feature Importances (Tuned Model):")
print(shap_importance.to_string(index=False))

# Generate a summary plot and save it to an image
shap.summary_plot(shap_values, X_test, show=False)
plt.savefig('shap_summary_tuned.png', bbox_inches='tight')
print("SHAP summary plot saved to shap_summary_tuned.png")
