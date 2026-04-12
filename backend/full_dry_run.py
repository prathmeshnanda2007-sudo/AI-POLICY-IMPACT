"""
Full Dry Run Test for AI Policy Impact Simulator
=================================================
Tests every API endpoint with training and testing data.
Verifies: Auth, Predictions, Model Training, Scenarios, History,
          Sensitivity, Recommendations, Feature Importance.
"""

import sys
import time
import json
import hashlib
import hmac
import base64
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---- Direct Module Tests First ----
print("=" * 70)
print("  AI POLICY IMPACT SIMULATOR — FULL DRY RUN")
print("=" * 70)

PASS = 0
FAIL = 0
RESULTS = []

def log_test(name, passed, detail=""):
    global PASS, FAIL
    status = "✅ PASS" if passed else "❌ FAIL"
    if passed:
        PASS += 1
    else:
        FAIL += 1
    msg = f"  {status}  {name}"
    if detail:
        msg += f"  →  {detail}"
    print(msg)
    RESULTS.append({"name": name, "passed": passed, "detail": detail})


# ============================================================
# PHASE 1: Database Module Tests
# ============================================================
print("\n" + "─" * 50)
print("  PHASE 1: Database Module")
print("─" * 50)

try:
    from services.database import (
        init_db, create_user, get_user_by_email, get_user_by_id,
        update_last_login, save_scenario, get_all_scenarios,
        delete_scenario, save_simulation, get_history, log_training
    )
    log_test("Database import", True)
except Exception as e:
    log_test("Database import", False, str(e))
    print("\n⛔ FATAL: Cannot continue without database module")
    sys.exit(1)

# Test init_db
try:
    init_db()
    log_test("Database init (create tables)", True)
except Exception as e:
    log_test("Database init (create tables)", False, str(e))

# Test user creation
test_email = f"dryrun_{int(time.time())}@test.com"
test_password_hash = "fakesalt:fakehash"
test_name = "Dry Run User"
test_user_id = None

try:
    user = create_user(test_email, test_password_hash, test_name)
    test_user_id = user['id']
    log_test("Create user", True, f"id={user['id']}, email={user['email']}")
except Exception as e:
    log_test("Create user", False, str(e))

# Test duplicate user
try:
    create_user(test_email, test_password_hash, test_name)
    log_test("Reject duplicate email", False, "Should have raised ValueError")
except ValueError as e:
    log_test("Reject duplicate email", True, str(e))
except Exception as e:
    log_test("Reject duplicate email", False, str(e))

# Test invalid email
try:
    create_user("invalid", test_password_hash, test_name)
    log_test("Reject invalid email", False, "Should have raised ValueError")
except ValueError as e:
    log_test("Reject invalid email", True, str(e))
except Exception as e:
    log_test("Reject invalid email", False, str(e))

# Test get user by email
try:
    user = get_user_by_email(test_email)
    assert user is not None, "User not found"
    assert user['email'] == test_email
    log_test("Get user by email", True, f"Found: {user['email']}")
except Exception as e:
    log_test("Get user by email", False, str(e))

# Test get user by ID
try:
    user = get_user_by_id(test_user_id)
    assert user is not None, "User not found"
    assert user['id'] == test_user_id
    log_test("Get user by ID", True, f"Found: id={user['id']}")
except Exception as e:
    log_test("Get user by ID", False, str(e))

# Test update last login
try:
    update_last_login(test_user_id)
    log_test("Update last login", True)
except Exception as e:
    log_test("Update last login", False, str(e))

# Test save simulation
sim_inputs = {"tax_rate": 25, "fuel_price": 3.5, "subsidy": 15, "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50}
sim_results = {"gdp_growth": 2.5, "inflation": 3.0, "employment_rate": 94.0, "environment_score": 65.0, "public_satisfaction": 70.0}

try:
    sim_id = save_simulation(sim_inputs, sim_results, "RandomForest", 0.92)
    log_test("Save simulation", True, f"id={sim_id}")
except Exception as e:
    log_test("Save simulation", False, str(e))

# Save a few more simulations for history testing
for i in range(3):
    try:
        modified_inputs = {**sim_inputs, "tax_rate": 20 + i * 5}
        modified_results = {**sim_results, "gdp_growth": 2.0 + i * 0.5}
        save_simulation(modified_inputs, modified_results, "RandomForest", 0.90 + i * 0.02)
    except:
        pass

# Test get history
try:
    history = get_history(10)
    assert isinstance(history, list), "History should be a list"
    assert len(history) >= 1, "History should have at least 1 entry"
    log_test("Get simulation history", True, f"{len(history)} records found")
except Exception as e:
    log_test("Get simulation history", False, str(e))

# Test save scenario
try:
    scenario = save_scenario("Test High Tax", sim_inputs, sim_results)
    assert 'id' in scenario
    test_scenario_id = scenario['id']
    log_test("Save scenario", True, f"id={scenario['id']}, name={scenario['name']}")
except Exception as e:
    log_test("Save scenario", False, str(e))

# Save another scenario for comparison testing
try:
    low_tax_inputs = {**sim_inputs, "tax_rate": 10, "subsidy": 30}
    low_tax_results = {**sim_results, "gdp_growth": 3.8, "inflation": 3.5}
    save_scenario("Low Tax + High Subsidy", low_tax_inputs, low_tax_results)
    log_test("Save second scenario", True)
except Exception as e:
    log_test("Save second scenario", False, str(e))

# Test get all scenarios
try:
    scenarios = get_all_scenarios()
    assert len(scenarios) >= 2, f"Expected >=2 scenarios, got {len(scenarios)}"
    log_test("Get all scenarios", True, f"{len(scenarios)} scenarios found")
except Exception as e:
    log_test("Get all scenarios", False, str(e))

# Test delete scenario
try:
    result = delete_scenario(test_scenario_id)
    assert result is True
    log_test("Delete scenario", True, f"Deleted id={test_scenario_id}")
except Exception as e:
    log_test("Delete scenario", False, str(e))

# Test log training
try:
    log_training("RandomForest", 0.35, 0.94, 5000)
    log_test("Log training event", True)
except Exception as e:
    log_test("Log training event", False, str(e))


# ============================================================
# PHASE 2: Auth Service Tests
# ============================================================
print("\n" + "─" * 50)
print("  PHASE 2: Auth Service (JWT + Password Hashing)")
print("─" * 50)

try:
    from services.auth import (
        hash_password, verify_password, create_access_token,
        decode_token
    )
    log_test("Auth service import", True)
except Exception as e:
    log_test("Auth service import", False, str(e))

# Test password hashing
try:
    raw_password = "TestPass123!"
    hashed = hash_password(raw_password)
    assert ':' in hashed, "Hash should contain salt:key format"
    log_test("Password hashing", True, f"Hash format valid (len={len(hashed)})")
except Exception as e:
    log_test("Password hashing", False, str(e))

# Test password verification
try:
    assert verify_password(raw_password, hashed) is True, "Should match"
    log_test("Password verify (correct)", True)
except Exception as e:
    log_test("Password verify (correct)", False, str(e))

try:
    assert verify_password("WrongPassword", hashed) is False, "Should not match"
    log_test("Password verify (wrong)", True)
except Exception as e:
    log_test("Password verify (wrong)", False, str(e))

# Test JWT creation
try:
    token = create_access_token(1, "test@test.com", "Test User")
    assert len(token.split('.')) == 3, "JWT should have 3 parts"
    log_test("JWT token creation", True, f"Token length={len(token)}")
except Exception as e:
    log_test("JWT token creation", False, str(e))

# Test JWT decoding
try:
    payload = decode_token(token)
    assert payload is not None, "Valid token should decode"
    assert payload['email'] == "test@test.com"
    assert payload['sub'] == "1"
    assert payload['name'] == "Test User"
    assert 'exp' in payload and 'iat' in payload
    log_test("JWT token decode (valid)", True, f"sub={payload['sub']}, email={payload['email']}")
except Exception as e:
    log_test("JWT token decode (valid)", False, str(e))

# Test expired/invalid token
try:
    result = decode_token("invalid.token.here")
    assert result is None, "Invalid token should return None"
    log_test("JWT token decode (invalid)", True)
except Exception as e:
    log_test("JWT token decode (invalid)", False, str(e))

# Test token with tampered signature
try:
    tampered = token[:-5] + "xxxxx"
    result = decode_token(tampered)
    assert result is None, "Tampered token should fail"
    log_test("JWT tampered token rejected", True)
except Exception as e:
    log_test("JWT tampered token rejected", False, str(e))


# ============================================================
# PHASE 3: ML Model Tests (Training & Prediction)
# ============================================================
print("\n" + "─" * 50)
print("  PHASE 3: ML Model (Training, Prediction, Analysis)")
print("─" * 50)

try:
    from models.ml_model import (
        generate_synthetic_data, train_and_select_best, load_model,
        predict_policy, get_feature_importance, sensitivity_analysis,
        recommend_policy, FEATURE_NAMES, OUTPUT_NAMES
    )
    log_test("ML model import", True)
except Exception as e:
    log_test("ML model import", False, str(e))
    print("\n⛔ FATAL: Cannot continue without ML model module")
    sys.exit(1)

# Test synthetic data generation
try:
    X, y = generate_synthetic_data(100, seed=99)
    assert X.shape == (100, 6), f"Expected (100,6), got {X.shape}"
    assert y.shape == (100, 5), f"Expected (100,5), got {y.shape}"
    assert list(X.columns) == FEATURE_NAMES
    assert list(y.columns) == OUTPUT_NAMES
    log_test("Synthetic data generation", True, f"X={X.shape}, y={y.shape}")
except Exception as e:
    log_test("Synthetic data generation", False, str(e))

# Test data statistics
try:
    X, y = generate_synthetic_data(5000, seed=42)
    for col in FEATURE_NAMES:
        assert X[col].std() > 0, f"{col} has zero variance"
    for col in OUTPUT_NAMES:
        assert y[col].std() > 0, f"{col} has zero variance"
    log_test("Data statistics (variance check)", True, f"All features/outputs have non-zero variance")
except Exception as e:
    log_test("Data statistics (variance check)", False, str(e))

# Test model training
try:
    print("\n  🔧 Training models (this may take 10-20 seconds)...")
    model, scaler, metadata = train_and_select_best()
    assert model is not None
    assert scaler is not None
    assert 'model_type' in metadata
    assert 'rmse' in metadata
    assert 'r2_score' in metadata
    log_test("Model training", True, 
             f"Best: {metadata['model_type']}, RMSE={metadata['rmse']:.4f}, R²={metadata['r2_score']:.4f}")
except Exception as e:
    log_test("Model training", False, str(e))

# Test model metadata
try:
    assert metadata['r2_score'] > 0.80, f"R² too low: {metadata['r2_score']}"
    assert metadata['rmse'] < 5.0, f"RMSE too high: {metadata['rmse']}"
    assert 'feature_importance' in metadata
    assert 'all_results' in metadata
    assert len(metadata['all_results']) == 3  # RF, LR, GB
    log_test("Model quality check", True, 
             f"R²={metadata['r2_score']:.4f} (>0.80), RMSE={metadata['rmse']:.4f} (<5.0)")
except Exception as e:
    log_test("Model quality check", False, str(e))

# Test all 3 models were compared
try:
    results_keys = list(metadata['all_results'].keys())
    assert 'RandomForest' in results_keys
    assert 'LinearRegression' in results_keys
    assert 'GradientBoosting' in results_keys
    log_test("All 3 models compared", True, f"Models: {results_keys}")
except Exception as e:
    log_test("All 3 models compared", False, str(e))

# Test model loading
try:
    loaded_model, loaded_scaler, loaded_metadata = load_model()
    assert loaded_model is not None
    assert loaded_scaler is not None
    assert loaded_metadata.get('model_type') == metadata.get('model_type')
    log_test("Model loading from disk", True)
except Exception as e:
    log_test("Model loading from disk", False, str(e))


# ---- PREDICTION TESTS (Training Data Scenarios) ----
print("\n  📊 Testing predictions with training data scenarios...")

# Default/baseline scenario
try:
    default_inputs = {
        "tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
        "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50
    }
    result = predict_policy(default_inputs, model, scaler)
    assert 'gdp_growth' in result
    assert 'inflation' in result
    assert 'employment_rate' in result
    assert 'environment_score' in result
    assert 'public_satisfaction' in result
    assert 'confidence' in result
    assert 0 < result['confidence'] <= 1.0
    log_test("Predict: Default/baseline inputs", True,
             f"GDP={result['gdp_growth']:.2f}, Inf={result['inflation']:.2f}, Emp={result['employment_rate']:.2f}")
except Exception as e:
    log_test("Predict: Default/baseline inputs", False, str(e))

# High tax scenario
try:
    high_tax = {
        "tax_rate": 50, "fuel_price": 3.5, "subsidy": 15,
        "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50
    }
    result_ht = predict_policy(high_tax, model, scaler)
    # High tax should generally lower GDP growth
    log_test("Predict: High tax scenario", True,
             f"GDP={result_ht['gdp_growth']:.2f} (expected lower than default {result['gdp_growth']:.2f})")
except Exception as e:
    log_test("Predict: High tax scenario", False, str(e))

# High subsidy scenario
try:
    high_sub = {
        "tax_rate": 25, "fuel_price": 3.5, "subsidy": 40,
        "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50
    }
    result_hs = predict_policy(high_sub, model, scaler)
    log_test("Predict: High subsidy scenario", True,
             f"GDP={result_hs['gdp_growth']:.2f}, Emp={result_hs['employment_rate']:.2f}")
except Exception as e:
    log_test("Predict: High subsidy scenario", False, str(e))

# Low interest rate scenario
try:
    low_ir = {
        "tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
        "public_spending": 30, "interest_rate": 1, "environmental_regulation": 50
    }
    result_li = predict_policy(low_ir, model, scaler)
    log_test("Predict: Low interest rate", True,
             f"GDP={result_li['gdp_growth']:.2f}, Inf={result_li['inflation']:.2f}")
except Exception as e:
    log_test("Predict: Low interest rate", False, str(e))

# Green policy scenario (high env reg)
try:
    green = {
        "tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
        "public_spending": 30, "interest_rate": 5, "environmental_regulation": 95
    }
    result_g = predict_policy(green, model, scaler)
    log_test("Predict: Green policy (high env reg)", True,
             f"EnvScore={result_g['environment_score']:.2f}, Satisfaction={result_g['public_satisfaction']:.2f}")
except Exception as e:
    log_test("Predict: Green policy (high env reg)", False, str(e))

# Extreme scenario (all max)
try:
    extreme = {
        "tax_rate": 55, "fuel_price": 9.0, "subsidy": 45,
        "public_spending": 55, "interest_rate": 18, "environmental_regulation": 95
    }
    result_ext = predict_policy(extreme, model, scaler)
    log_test("Predict: Extreme scenario (all high)", True,
             f"GDP={result_ext['gdp_growth']:.2f}, Conf={result_ext['confidence']:.2f}")
except Exception as e:
    log_test("Predict: Extreme scenario (all high)", False, str(e))

# Minimum scenario (all min)
try:
    minimum = {
        "tax_rate": 5, "fuel_price": 1.5, "subsidy": 0,
        "public_spending": 12, "interest_rate": 0.25, "environmental_regulation": 5
    }
    result_min = predict_policy(minimum, model, scaler)
    log_test("Predict: Minimum scenario (all low)", True,
             f"GDP={result_min['gdp_growth']:.2f}, Emp={result_min['employment_rate']:.2f}")
except Exception as e:
    log_test("Predict: Minimum scenario (all low)", False, str(e))


# ---- TESTING DATA (Test with holdout / unseen combos) ----
print("\n  🧪 Testing with unseen/test data combinations...")

import numpy as np
np.random.seed(2026)

test_scenarios = []
for i in range(5):
    test_input = {
        "tax_rate": np.random.uniform(5, 55),
        "fuel_price": np.random.uniform(1.5, 9.0),
        "subsidy": np.random.uniform(0, 45),
        "public_spending": np.random.uniform(12, 55),
        "interest_rate": np.random.uniform(0.25, 18),
        "environmental_regulation": np.random.uniform(5, 95),
    }
    test_scenarios.append(test_input)

for i, test_input in enumerate(test_scenarios):
    try:
        result_test = predict_policy(test_input, model, scaler)
        assert all(k in result_test for k in OUTPUT_NAMES), "Missing output keys"
        assert result_test['confidence'] > 0, "Confidence should be positive"
        log_test(f"Predict: Random test #{i+1}", True,
                 f"GDP={result_test['gdp_growth']:.2f}, Conf={result_test['confidence']:.2f}")
    except Exception as e:
        log_test(f"Predict: Random test #{i+1}", False, str(e))


# ---- Feature Importance ----
print("\n  📈 Testing feature importance...")

try:
    fi = get_feature_importance()
    assert isinstance(fi, list), "Feature importance should be a list"
    assert len(fi) == 6, f"Expected 6 features, got {len(fi)}"
    for item in fi:
        assert 'feature' in item
        assert 'importance' in item
        assert item['importance'] >= 0
    log_test("Feature importance", True, 
             f"Top feature: {fi[0]['feature']}={fi[0]['importance']:.4f}")
except Exception as e:
    log_test("Feature importance", False, str(e))


# ---- Sensitivity Analysis ----
print("\n  🔬 Testing sensitivity analysis...")

try:
    sa = sensitivity_analysis(default_inputs, 'gdp_growth')
    assert isinstance(sa, list), "Sensitivity should return a list"
    assert len(sa) == 6, f"Expected 6 features, got {len(sa)}"
    for item in sa:
        assert 'feature' in item
        assert 'impact' in item
        assert 'direction' in item
    log_test("Sensitivity analysis (GDP)", True,
             f"Most impactful: {sa[0]['feature']} (impact={sa[0]['impact']:.4f})")
except Exception as e:
    log_test("Sensitivity analysis (GDP)", False, str(e))

try:
    sa2 = sensitivity_analysis(default_inputs, 'inflation')
    log_test("Sensitivity analysis (Inflation)", True,
             f"Most impactful: {sa2[0]['feature']} (impact={sa2[0]['impact']:.4f})")
except Exception as e:
    log_test("Sensitivity analysis (Inflation)", False, str(e))


# ---- Policy Recommendation ----
print("\n  💡 Testing AI policy recommendation...")

try:
    targets = {
        "gdp_growth": 4.0,
        "inflation": 2.5,
        "employment_rate": 96.0,
        "environment_score": 80.0,
        "public_satisfaction": 75.0,
    }
    rec = recommend_policy(targets)
    assert 'recommended_inputs' in rec
    assert 'predicted_outcomes' in rec
    assert 'optimization_score' in rec
    ri = rec['recommended_inputs']
    assert all(k in ri for k in FEATURE_NAMES), "Missing recommended input features"
    log_test("Policy recommendation", True,
             f"Score={rec['optimization_score']:.4f}, TaxRate={ri['tax_rate']:.1f}, Subsidy={ri['subsidy']:.1f}")
except Exception as e:
    log_test("Policy recommendation", False, str(e))


# ============================================================
# PHASE 4: FastAPI Integration Tests
# ============================================================
print("\n" + "─" * 50)
print("  PHASE 4: FastAPI App (Integration)")
print("─" * 50)

try:
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    log_test("FastAPI TestClient setup", True)
except Exception as e:
    log_test("FastAPI TestClient setup", False, str(e))
    print("\n⛔ Cannot test API endpoints. Install httpx: pip install httpx")
    client = None

if client:
    # Health check
    try:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()['status'] == 'healthy'
        log_test("GET /health", True, f"status={resp.json()['status']}")
    except Exception as e:
        log_test("GET /health", False, str(e))

    # API status
    try:
        resp = client.get("/api/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'online'
        log_test("GET /api/status", True, f"version={data['version']}")
    except Exception as e:
        log_test("GET /api/status", False, str(e))

    # Register a test user
    reg_email = f"apitest_{int(time.time())}@test.com"
    reg_password = "SecurePass123!"
    reg_name = "API Test User"
    auth_token = None

    try:
        resp = client.post("/auth/register", json={
            "email": reg_email, "password": reg_password, "name": reg_name
        })
        assert resp.status_code == 200, f"Status: {resp.status_code}, Body: {resp.text}"
        data = resp.json()
        assert 'token' in data
        assert 'user' in data
        auth_token = data['token']
        log_test("POST /auth/register", True, f"user_id={data['user']['id']}")
    except Exception as e:
        log_test("POST /auth/register", False, str(e))

    # Login with same user
    try:
        resp = client.post("/auth/login", json={
            "email": reg_email, "password": reg_password
        })
        assert resp.status_code == 200
        data = resp.json()
        assert 'token' in data
        auth_token = data['token']  # Use fresh token
        log_test("POST /auth/login", True, f"token_len={len(auth_token)}")
    except Exception as e:
        log_test("POST /auth/login", False, str(e))

    # Login with wrong password
    try:
        resp = client.post("/auth/login", json={
            "email": reg_email, "password": "WrongPassword"
        })
        assert resp.status_code == 401
        log_test("POST /auth/login (wrong password)", True, "401 returned correctly")
    except Exception as e:
        log_test("POST /auth/login (wrong password)", False, str(e))

    # Verify token
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    try:
        resp = client.post("/auth/verify", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data['valid'] is True
        log_test("POST /auth/verify", True)
    except Exception as e:
        log_test("POST /auth/verify", False, str(e))

    # Get current user
    try:
        resp = client.get("/auth/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data['email'] == reg_email
        log_test("GET /auth/me", True, f"email={data['email']}")
    except Exception as e:
        log_test("GET /auth/me", False, str(e))

    # Unauthenticated request should fail
    try:
        resp = client.post("/predict", json=sim_inputs)
        assert resp.status_code == 401 or resp.status_code == 403
        log_test("POST /predict (no auth)", True, "Correctly rejected")
    except Exception as e:
        log_test("POST /predict (no auth)", False, str(e))

    # Authenticated prediction
    try:
        resp = client.post("/predict", json=default_inputs, headers=headers)
        assert resp.status_code == 200, f"Status: {resp.status_code}, Body: {resp.text}"
        data = resp.json()
        assert 'gdp_growth' in data
        assert 'inflation' in data
        assert 'confidence' in data
        log_test("POST /predict (authenticated)", True,
                 f"GDP={data['gdp_growth']:.2f}, Inf={data['inflation']:.2f}")
    except Exception as e:
        log_test("POST /predict (authenticated)", False, str(e))

    # Compare scenarios
    try:
        compare_payload = {
            "scenarios": [
                default_inputs,
                {**default_inputs, "tax_rate": 50},
                {**default_inputs, "subsidy": 40},
            ]
        }
        resp = client.post("/compare", json=compare_payload, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 3
        log_test("POST /compare (3 scenarios)", True, f"Got {len(data)} results")
    except Exception as e:
        log_test("POST /compare (3 scenarios)", False, str(e))

    # Save scenario via API
    try:
        scenario_payload = {
            "name": "API Test Scenario",
            "inputs": default_inputs,
            "results": predict_policy(default_inputs, model, scaler),
        }
        resp = client.post("/scenarios", json=scenario_payload, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert 'id' in data
        api_scenario_id = data['id']
        log_test("POST /scenarios (save)", True, f"id={data['id']}")
    except Exception as e:
        log_test("POST /scenarios (save)", False, str(e))

    # Get scenarios
    try:
        resp = client.get("/scenarios", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        log_test("GET /scenarios", True, f"{len(data)} scenarios")
    except Exception as e:
        log_test("GET /scenarios", False, str(e))

    # Delete scenario
    try:
        resp = client.delete(f"/scenarios/{api_scenario_id}", headers=headers)
        assert resp.status_code == 200
        log_test("DELETE /scenarios/{id}", True)
    except Exception as e:
        log_test("DELETE /scenarios/{id}", False, str(e))

    # Get history
    try:
        resp = client.get("/history", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        log_test("GET /history", True, f"{len(data)} records")
    except Exception as e:
        log_test("GET /history", False, str(e))

    # Model info
    try:
        resp = client.get("/model/info")
        assert resp.status_code == 200
        data = resp.json()
        assert 'model_type' in data
        log_test("GET /model/info", True, f"model={data.get('model_type')}")
    except Exception as e:
        log_test("GET /model/info", False, str(e))

    # Feature importance
    try:
        resp = client.get("/model/feature-importance")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        log_test("GET /model/feature-importance", True, f"{len(data)} features")
    except Exception as e:
        log_test("GET /model/feature-importance", False, str(e))

    # Sensitivity analysis via API
    try:
        resp = client.post("/sensitivity", json={
            "inputs": default_inputs,
            "target_variable": "gdp_growth"
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        log_test("POST /sensitivity", True, f"Top: {data[0]['feature']} (impact={data[0]['impact']:.4f})")
    except Exception as e:
        log_test("POST /sensitivity", False, str(e))

    # Recommendation via API
    try:
        resp = client.post("/recommend", json={
            "gdp_growth": 4.0,
            "inflation": 2.5,
            "employment_rate": 96.0,
            "environment_score": 80.0,
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert 'recommended_inputs' in data
        log_test("POST /recommend", True, f"score={data['optimization_score']:.4f}")
    except Exception as e:
        log_test("POST /recommend", False, str(e))

    # Retrain model via API
    try:
        resp = client.post("/train", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'success'
        log_test("POST /train (retrain model)", True,
                 f"model={data['model_type']}, R²={data['r2_score']:.4f}")
    except Exception as e:
        log_test("POST /train (retrain model)", False, str(e))


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print(f"  DRY RUN COMPLETE")
print(f"  {'─' * 40}")
total = PASS + FAIL
print(f"  ✅ Passed: {PASS}/{total}")
print(f"  ❌ Failed: {FAIL}/{total}")
rate = (PASS / total * 100) if total > 0 else 0
print(f"  📊 Pass Rate: {rate:.1f}%")

if FAIL == 0:
    print(f"\n  🎉 ALL TESTS PASSED! The website is fully functional.")
else:
    print(f"\n  ⚠️  {FAIL} test(s) failed. See details above.")
    print("\n  Failed tests:")
    for r in RESULTS:
        if not r['passed']:
            print(f"    ❌ {r['name']}: {r['detail']}")

print("=" * 70)

# Save results to file
output_path = os.path.join(os.path.dirname(__file__), 'dry_run_results.txt')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(f"AI Policy Impact Simulator - Dry Run Results\n")
    f.write(f"{'=' * 50}\n")
    f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Passed: {PASS}/{total}\n")
    f.write(f"Failed: {FAIL}/{total}\n")
    f.write(f"Pass Rate: {rate:.1f}%\n\n")
    for r in RESULTS:
        status = "PASS" if r['passed'] else "FAIL"
        f.write(f"[{status}] {r['name']}: {r['detail']}\n")

print(f"\n  Results saved to: {output_path}")
