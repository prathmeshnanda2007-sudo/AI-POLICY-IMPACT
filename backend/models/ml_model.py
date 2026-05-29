import pandas as pd
import numpy as np
import joblib
import os
import json
import logging

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(MODEL_DIR, '..'))
MODEL_PATH = os.path.join(BACKEND_DIR, 'model.pkl')
METADATA_PATH = os.path.join(BACKEND_DIR, 'model_metadata.json')

FEATURE_NAMES = [
    'Tax_Rate', 
    'Fuel_Price', 
    'Subsidy_Level', 
    'Public_Spending', 
    'Interest_Rate', 
    'Environmental_Regulation'
]

OUTPUT_NAMES = [
    'gdp_growth', 
    'inflation', 
    'employment_rate', 
    'environment_score', 
    'public_satisfaction'
]

def load_model():
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        metadata = {}
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, 'r') as f:
                metadata = json.load(f)
        return model, None, metadata
    else:
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}.")

def predict_policy(input_data: dict, model=None, scaler=None):
    if model is None:
        model, _, _ = load_model()
        
    feature_dict = {}
    for f in FEATURE_NAMES:
        feature_dict[f] = [input_data.get(f, 0)]
        
    df_features = pd.DataFrame(feature_dict)[FEATURE_NAMES]
    prediction = model.predict(df_features)[0] 
    
    return {
        'gdp_growth': round(float(prediction[0]), 4),
        'inflation': round(float(prediction[1]), 4),
        'employment_rate': round(float(prediction[2]), 4),
        'environment_score': round(float(prediction[3]), 4),
        'public_satisfaction': round(float(prediction[4]), 4),
        'confidence': 0.85
    }

def get_feature_importance():
    path = os.path.join(BACKEND_DIR, 'feature_importance.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return [
        {'feature': f, 'importance': 0.16} for f in FEATURE_NAMES
    ]

def sensitivity_analysis(base_inputs: dict, target_variable: str = 'gdp_growth'):
    model, _, _ = load_model()
    # Provide defaults
    defaults = {
        'Tax_Rate': 15.0, 'Fuel_Price': 4.5, 'Subsidy_Level': 10.0,
        'Public_Spending': 30.0, 'Interest_Rate': 5.0, 'Environmental_Regulation': 50.0
    }
    base_complete = {f: base_inputs.get(f, defaults[f]) for f in FEATURE_NAMES}

    base_pred = predict_policy(base_complete, model)
    base_val = base_pred.get(target_variable, 0)

    from copy import deepcopy
    results = []
    for feat in FEATURE_NAMES:
        modified = deepcopy(base_complete)
        original = modified.get(feat, 0)
        modified[feat] = original * 1.1 if original != 0 else 1.0
        new_pred = predict_policy(modified, model)
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
    model, _, _ = load_model()
    defaults = {
        'Tax_Rate': 15.0, 'Fuel_Price': 4.5, 'Subsidy_Level': 10.0,
        'Public_Spending': 30.0, 'Interest_Rate': 5.0, 'Environmental_Regulation': 50.0
    }
    
    def objective(x):
        feature_dict = {}
        for i, f in enumerate(FEATURE_NAMES):
            feature_dict[f] = [x[i]]
            
        pred = model.predict(pd.DataFrame(feature_dict)[FEATURE_NAMES])[0]
        
        # pred[0] is gdp_growth
        if 'gdp_growth' in target_outcomes:
            return ((pred[0] - target_outcomes['gdp_growth']) ** 2)
        return 0

    bounds = [
        (0, 60),      # Tax_Rate
        (1, 10),      # Fuel_Price
        (0, 50),      # Subsidy_Level
        (10, 60),     # Public_Spending
        (0, 20),      # Interest_Rate
        (0, 100)      # Environmental_Regulation
    ]
    
    from scipy.optimize import minimize
    import numpy as np
    
    best_score = float('inf')
    best_x = None
    for _ in range(3):
        x0 = [np.random.uniform(b[0], b[1]) for b in bounds]
        res = minimize(objective, x0, method='L-BFGS-B', bounds=bounds)
        if res.fun < best_score:
            best_score = res.fun
            best_x = res.x

    best_inputs = {
        FEATURE_NAMES[i]: round(best_x[i], 2) for i in range(len(FEATURE_NAMES))
    }
    best_predictions = predict_policy(best_inputs, model)

    return {
        'recommended_inputs': best_inputs,
        'predicted_outcomes': {k: round(v, 4) for k, v in best_predictions.items() if k != 'confidence'},
        'optimization_score': round(best_score, 4),
    }

def train_and_select_best():
    import subprocess
    subprocess.run(["python", "train_model.py"], cwd=BACKEND_DIR)
    return load_model()
