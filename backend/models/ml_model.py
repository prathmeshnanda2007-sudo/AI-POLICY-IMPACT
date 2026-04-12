"""
AI Policy Impact Simulator — ML Model Training & Prediction

Generates synthetic dataset, trains RandomForest/LinearRegression/GradientBoosting,
selects best model by RMSE, and saves to model.pkl
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'data')
MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
METADATA_PATH = os.path.join(MODEL_DIR, 'model_metadata.json')

FEATURE_NAMES = [
    'tax_rate', 'fuel_price', 'subsidy',
    'public_spending', 'interest_rate', 'environmental_regulation'
]

OUTPUT_NAMES = [
    'gdp_growth', 'inflation', 'employment_rate',
    'environment_score', 'public_satisfaction'
]


def generate_synthetic_data(n_samples=5000, seed=42):
    """Generate realistic synthetic policy→outcome data with non-linear relationships."""
    np.random.seed(seed)

    # Features
    tax_rate = np.random.uniform(5, 55, n_samples)
    fuel_price = np.random.uniform(1.5, 9.0, n_samples)
    subsidy = np.random.uniform(0, 45, n_samples)
    public_spending = np.random.uniform(12, 55, n_samples)
    interest_rate = np.random.uniform(0.25, 18, n_samples)
    env_regulation = np.random.uniform(5, 95, n_samples)

    # --- Realistic non-linear output relationships ---
    
    # GDP Growth: Higher tax hurts, subsidy helps, moderate spending optimal, high interest hurts
    gdp_growth = (
        3.5
        - 0.06 * tax_rate
        + 0.04 * subsidy
        + 0.03 * public_spending
        - 0.002 * public_spending ** 1.3
        - 0.12 * interest_rate
        + 0.005 * interest_rate ** 0.5 * subsidy
        - 0.01 * env_regulation
        - 0.02 * fuel_price
        + np.random.normal(0, 0.3, n_samples)
    )

    # Inflation: Spending and subsidy increase it, higher interest reduces it
    inflation = (
        2.0
        + 0.04 * public_spending
        + 0.03 * subsidy
        + 0.15 * fuel_price
        - 0.08 * interest_rate
        + 0.01 * tax_rate
        + 0.003 * public_spending * subsidy / 100
        + np.random.normal(0, 0.25, n_samples)
    )

    # Employment: Subsidy and public spending help, high tax and interest hurt
    employment_rate = (
        92.0
        - 0.08 * tax_rate
        + 0.12 * subsidy
        + 0.06 * public_spending
        - 0.15 * interest_rate
        + 0.02 * env_regulation
        - 0.05 * fuel_price
        + np.random.normal(0, 0.5, n_samples)
    )
    employment_rate = np.clip(employment_rate, 70, 99.5)

    # Environment Score: Regulation helps most, fuel price inversely related, subsidy helps somewhat
    environment_score = (
        30.0
        + 0.45 * env_regulation
        - 0.8 * fuel_price
        + 0.1 * subsidy
        + 0.05 * tax_rate
        - 0.02 * public_spending
        - 0.5 * interest_rate * 0.3
        + np.random.normal(0, 2.0, n_samples)
    )
    environment_score = np.clip(environment_score, 5, 100)

    # Public Satisfaction: Complex mix — low tax, low fuel, high employment, good environment
    public_satisfaction = (
        60.0
        - 0.3 * tax_rate
        - 1.2 * fuel_price
        + 0.25 * subsidy
        + 0.1 * public_spending
        - 0.2 * interest_rate
        + 0.15 * env_regulation
        + 0.1 * (employment_rate - 90)
        - 0.05 * np.abs(inflation - 2.5)
        + np.random.normal(0, 1.5, n_samples)
    )
    public_satisfaction = np.clip(public_satisfaction, 10, 95)

    X = np.column_stack([tax_rate, fuel_price, subsidy, public_spending, interest_rate, env_regulation])
    y = np.column_stack([gdp_growth, inflation, employment_rate, environment_score, public_satisfaction])

    return pd.DataFrame(X, columns=FEATURE_NAMES), pd.DataFrame(y, columns=OUTPUT_NAMES)


def train_and_select_best():
    """Train multiple models, compare RMSE, save the best."""
    os.makedirs(MODEL_DIR, exist_ok=True)

    print("📊 Generating 5,000 synthetic policy samples...")
    X, y = generate_synthetic_data(5000)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        'RandomForest': MultiOutputRegressor(
            RandomForestRegressor(n_estimators=200, max_depth=15, min_samples_split=5, random_state=42, n_jobs=-1)
        ),
        'LinearRegression': MultiOutputRegressor(LinearRegression()),
        'GradientBoosting': MultiOutputRegressor(
            GradientBoostingRegressor(n_estimators=150, max_depth=8, learning_rate=0.1, random_state=42)
        ),
    }

    results = {}
    for name, model in models.items():
        print(f"\n🔧 Training {name}...")
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        results[name] = {'model': model, 'rmse': rmse, 'r2': r2}
        print(f"   RMSE: {rmse:.4f}  |  R²: {r2:.4f}")

    # Select best by RMSE
    best_name = min(results, key=lambda k: results[k]['rmse'])
    best = results[best_name]
    print(f"\n✅ Best model: {best_name} (RMSE: {best['rmse']:.4f}, R²: {best['r2']:.4f})")

    # Save model and scaler
    joblib.dump(best['model'], MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    # Feature importance - use permutation importance for any model type
    from sklearn.inspection import permutation_importance
    print("\n📈 Computing feature importance...")
    perm_importance = permutation_importance(best['model'], X_test_scaled, y_test, n_repeats=10, random_state=42, n_jobs=-1)
    feature_importance = {}
    for j, feat in enumerate(FEATURE_NAMES):
        feature_importance[feat] = float(max(0, perm_importance.importances_mean[j]))

    # Save metadata
    metadata = {
        'model_type': best_name,
        'rmse': float(best['rmse']),
        'r2_score': float(best['r2']),
        'training_samples': 5000,
        'feature_names': FEATURE_NAMES,
        'output_names': OUTPUT_NAMES,
        'feature_importance': feature_importance,
        'all_results': {k: {'rmse': float(v['rmse']), 'r2': float(v['r2'])} for k, v in results.items()},
    }
    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n💾 Model saved to {MODEL_PATH}")
    print(f"   Scaler saved to {SCALER_PATH}")
    print(f"   Metadata saved to {METADATA_PATH}")
    return best['model'], scaler, metadata


def load_model():
    """Load trained model and scaler, or train if not found."""
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        metadata = {}
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH) as f:
                metadata = json.load(f)
        return model, scaler, metadata
    else:
        return train_and_select_best()


def predict_policy(input_data: dict, model=None, scaler=None):
    """Make prediction from policy input dictionary."""
    if model is None or scaler is None:
        model, scaler, _ = load_model()

    features = pd.DataFrame([[input_data.get(f, 0) for f in FEATURE_NAMES]], columns=FEATURE_NAMES)
    features_scaled = scaler.transform(features)
    predictions = model.predict(features_scaled)[0]

    # Calculate confidence based on how close inputs are to training distribution center
    center = scaler.mean_
    scale = scaler.scale_
    normalized_dist = np.mean(np.abs((features.values[0] - center) / scale))
    confidence = max(0.6, min(0.99, 1.0 - normalized_dist * 0.1))

    result = {}
    for i, name in enumerate(OUTPUT_NAMES):
        result[name] = float(predictions[i])
    result['confidence'] = float(confidence)

    return result


def get_feature_importance():
    """Return feature importance from saved metadata."""
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH) as f:
            metadata = json.load(f)
        fi = metadata.get('feature_importance', {})
        return [{'feature': k, 'importance': round(v, 4)} for k, v in sorted(fi.items(), key=lambda x: -x[1])]
    return []


def sensitivity_analysis(base_inputs: dict, target_variable: str = 'gdp_growth'):
    """Vary each input and measure impact on target variable."""
    model, scaler, _ = load_model()
    base_pred = predict_policy(base_inputs, model, scaler)
    base_val = base_pred.get(target_variable, 0)

    from copy import deepcopy
    results = []
    for feat in FEATURE_NAMES:
        modified = deepcopy(base_inputs)
        # Increase by 10%
        original = modified.get(feat, 0)
        modified[feat] = original * 1.1 if original != 0 else 1.0
        new_pred = predict_policy(modified, model, scaler)
        new_val = new_pred.get(target_variable, 0)
        impact = new_val - base_val
        results.append({
            'feature': feat,
            'base_value': original,
            'modified_value': modified[feat],
            'impact': round(impact, 4),
            'direction': 'positive' if impact > 0 else 'negative',
        })

    return sorted(results, key=lambda x: -abs(x['impact']))


def recommend_policy(target_outcomes: dict):
    """Simple grid search over policy space to find inputs closest to desired outcomes."""
    model, scaler, _ = load_model()
    
    best_score = float('inf')
    best_inputs = None
    best_predictions = None

    np.random.seed(123)
    # Random search over 2000 candidate policies
    for _ in range(2000):
        candidate = {
            'tax_rate': np.random.uniform(5, 55),
            'fuel_price': np.random.uniform(1.5, 9.0),
            'subsidy': np.random.uniform(0, 45),
            'public_spending': np.random.uniform(12, 55),
            'interest_rate': np.random.uniform(0.25, 18),
            'environmental_regulation': np.random.uniform(5, 95),
        }
        pred = predict_policy(candidate, model, scaler)
        
        score = 0
        for key, target_val in target_outcomes.items():
            if key in pred:
                score += (pred[key] - target_val) ** 2
        
        if score < best_score:
            best_score = score
            best_inputs = candidate
            best_predictions = pred

    # Round inputs
    for k in best_inputs:
        best_inputs[k] = round(best_inputs[k], 2)

    return {
        'recommended_inputs': best_inputs,
        'predicted_outcomes': {k: round(v, 4) for k, v in best_predictions.items() if k != 'confidence'},
        'optimization_score': round(best_score, 4),
    }


if __name__ == '__main__':
    train_and_select_best()
