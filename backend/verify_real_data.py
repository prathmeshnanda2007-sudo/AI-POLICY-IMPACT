import os
import sys

# Add backend dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.ml_model import predict_policy, load_model
from services.database import save_simulation, get_history, engine

def run_checks():
    print("==========================================================")
    print("      REAL DATA & NEON DB VALIDATION DRY RUN")
    print("==========================================================")
    
    print(f"\n[INFO] Database URL: {engine.url}")
    if "neon.tech" in str(engine.url):
        print("[SUCCESS] Confirmed: Connected to NeonDB!")
    else:
        print("[WARNING] Not connected to NeonDB!")

    model, scaler, metadata = load_model()
    print(f"[INFO] Loaded model: {metadata.get('model_type', 'Unknown')} with R2: {metadata.get('r2_score', 'Unknown')}")

    # 1. Test Prediction (Training Data Scenario - Typical Values)
    print("\n>>> 1. Testing Model with Training-like Data (Typical India Stats)")
    inputs_train = {
        "Inflation_CPI": 5.0,
        "Tax_Revenue_Pct_GDP": 15.0,
        "Unemployment_Pct": 7.0,
        "CO2_Emissions": 2500000,
        "FDI_Net_Inflows_Pct_GDP": 2.0
    }
    
    try:
        res_train = predict_policy(inputs_train, model, scaler)
        print(f"[SUCCESS] Prediction successful! Predicted GDP Growth: {res_train['gdp_growth']}%")
    except Exception as e:
        print(f"[ERROR] Exception during prediction: {e}")
        res_train = None

    # 2. Test Prediction (Testing Data Scenario - Extreme Values)
    print("\n>>> 2. Testing Model with Extreme/Stress Data")
    inputs_test = {
        "Inflation_CPI": 15.0,
        "Tax_Revenue_Pct_GDP": 25.0,
        "Unemployment_Pct": 15.0,
        "CO2_Emissions": 4000000,
        "FDI_Net_Inflows_Pct_GDP": -1.0
    }
    
    try:
        res_test = predict_policy(inputs_test, model, scaler)
        print(f"[SUCCESS] Prediction successful! Predicted GDP Growth: {res_test['gdp_growth']}%")
    except Exception as e:
        print(f"[ERROR] Exception during prediction: {e}")
        res_test = None

    # 3. Check Database Storage
    print("\n>>> 3. Checking NeonDB Database Storage")
    try:
        if res_test:
            sid = save_simulation(
                inputs=inputs_test, 
                results={"gdp_growth": res_test['gdp_growth']}, 
                model_type=metadata.get('model_type', "RandomForest"), 
                confidence=res_test.get('confidence', 0.85)
            )
            print(f"[SUCCESS] Successfully saved stress-test simulation to NeonDB (Sim ID: {sid})")
        
        history = get_history(limit=3)
        print(f"[SUCCESS] Retrieved {len(history)} recent simulations from NeonDB:")
        for h in history:
            print(f"   - [ID {h.get('id')}] Date: {h.get('timestamp')} | GDP: {h.get('results', {}).get('gdp_growth', 'N/A')}%")
            print(f"     Inputs: {h.get('inputs')}")
            
    except Exception as e:
        print(f"[ERROR] Database operation failed: {e}")
        
    print("\n==========================================================")
    print("                  DRY RUN COMPLETE")
    print("==========================================================")

if __name__ == '__main__':
    run_checks()
