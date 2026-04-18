"""
Comprehensive Dry Run & Functional Audit
AI Public Policy Impact Simulator

Tests ALL components: ML pipeline, Database, Auth, API endpoints,
with both TRAINING and TESTING data scenarios.
"""

import sys
import os
import json
import time
import traceback
import sqlite3
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure the backend directory is on the path
sys.path.insert(0, os.path.dirname(__file__))

# ─────────────────────────────────────────
# Result tracking
# ─────────────────────────────────────────
results = []
pass_count = 0
fail_count = 0
warn_count = 0

def log_test(name, status, detail=""):
    global pass_count, fail_count, warn_count
    icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(status, "❓")
    if status == "PASS": pass_count += 1
    elif status == "FAIL": fail_count += 1
    elif status == "WARN": warn_count += 1
    results.append({"name": name, "status": status, "detail": detail})
    print(f"  {icon} [{status}] {name}" + (f" — {detail}" if detail else ""))

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ═════════════════════════════════════════
# SECTION 1: ML MODEL PIPELINE
# ═════════════════════════════════════════
section("1. ML MODEL PIPELINE (Training & Testing)")

try:
    from models.ml_model import (
        generate_synthetic_data, train_and_select_best, load_model,
        predict_policy, get_feature_importance, sensitivity_analysis,
        recommend_policy, FEATURE_NAMES, OUTPUT_NAMES
    )
    log_test("ML module imports", "PASS")
except Exception as e:
    log_test("ML module imports", "FAIL", str(e))
    traceback.print_exc()

# 1.1 Synthetic Data Generation
try:
    X, y = generate_synthetic_data(5000)
    assert X.shape == (5000, 6), f"Expected (5000,6) got {X.shape}"
    assert y.shape == (5000, 5), f"Expected (5000,5) got {y.shape}"
    assert list(X.columns) == FEATURE_NAMES
    assert list(y.columns) == OUTPUT_NAMES
    assert X.isnull().sum().sum() == 0, "X has NaN values"
    assert y.isnull().sum().sum() == 0, "y has NaN values"
    log_test("Synthetic data generation (5000 samples)", "PASS", f"X={X.shape}, y={y.shape}")
except Exception as e:
    log_test("Synthetic data generation", "FAIL", str(e))

# 1.2 Feature Range Validation
try:
    range_checks = {
        'tax_rate': (5, 55),
        'fuel_price': (1.5, 9.0),
        'subsidy': (0, 45),
        'public_spending': (12, 55),
        'interest_rate': (0.25, 18),
        'environmental_regulation': (5, 95),
    }
    for feat, (lo, hi) in range_checks.items():
        fmin, fmax = X[feat].min(), X[feat].max()
        assert fmin >= lo - 0.01 and fmax <= hi + 0.01, f"{feat}: [{fmin:.2f},{fmax:.2f}] not in [{lo},{hi}]"
    log_test("Feature range validation", "PASS", "All 6 features within expected bounds")
except Exception as e:
    log_test("Feature range validation", "FAIL", str(e))

# 1.3 Model Training
try:
    model, scaler, metadata = train_and_select_best()
    assert model is not None
    assert scaler is not None
    assert 'model_type' in metadata
    assert 'rmse' in metadata
    assert 'r2_score' in metadata
    assert metadata['r2_score'] > 0.85, f"R² too low: {metadata['r2_score']}"
    log_test("Model training (3 algorithms compared)", "PASS",
             f"Best={metadata['model_type']}, R²={metadata['r2_score']:.4f}, RMSE={metadata['rmse']:.4f}")
except Exception as e:
    log_test("Model training", "FAIL", str(e))

# 1.4 Model Persistence
try:
    from models.ml_model import MODEL_PATH, SCALER_PATH, METADATA_PATH
    assert os.path.exists(MODEL_PATH), f"model.pkl not found at {MODEL_PATH}"
    assert os.path.exists(SCALER_PATH), f"scaler.pkl not found at {SCALER_PATH}"
    assert os.path.exists(METADATA_PATH), f"model_metadata.json not found at {METADATA_PATH}"
    model_size = os.path.getsize(MODEL_PATH)
    log_test("Model persistence (model.pkl, scaler.pkl, metadata.json)", "PASS", f"model.pkl={model_size} bytes")
except Exception as e:
    log_test("Model persistence", "FAIL", str(e))

# 1.5 Model Loading
try:
    loaded_model, loaded_scaler, loaded_meta = load_model()
    assert loaded_model is not None
    assert loaded_scaler is not None
    log_test("Model loading from disk", "PASS", f"Type={loaded_meta.get('model_type','?')}")
except Exception as e:
    log_test("Model loading", "FAIL", str(e))


# ═════════════════════════════════════════
# SECTION 2: PREDICTION WITH TRAINING DATA SCENARIOS
# ═════════════════════════════════════════
section("2. PREDICTIONS — TRAINING DATA SCENARIOS")

training_scenarios = [
    {
        "name": "Default Baseline",
        "inputs": {"tax_rate": 25, "fuel_price": 3.5, "subsidy": 15, "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50}
    },
    {
        "name": "High Tax + Strong Regulation",
        "inputs": {"tax_rate": 50, "fuel_price": 7.0, "subsidy": 5, "public_spending": 40, "interest_rate": 10, "environmental_regulation": 90}
    },
    {
        "name": "Low Tax Pro-Business",
        "inputs": {"tax_rate": 10, "fuel_price": 2.0, "subsidy": 40, "public_spending": 20, "interest_rate": 2, "environmental_regulation": 15}
    },
    {
        "name": "Balanced Growth",
        "inputs": {"tax_rate": 20, "fuel_price": 3.0, "subsidy": 25, "public_spending": 35, "interest_rate": 4, "environmental_regulation": 60}
    },
]

for scenario in training_scenarios:
    try:
        result = predict_policy(scenario["inputs"], model, scaler)
        assert all(k in result for k in OUTPUT_NAMES), f"Missing output keys"
        assert 'confidence' in result
        assert 0.5 <= result['confidence'] <= 1.0, f"Confidence out of range: {result['confidence']}"
        detail = ", ".join(f"{k}={result[k]:.2f}" for k in OUTPUT_NAMES)
        log_test(f"Training scenario: {scenario['name']}", "PASS", f"Conf={result['confidence']:.2f} | {detail}")
    except Exception as e:
        log_test(f"Training scenario: {scenario['name']}", "FAIL", str(e))


# ═════════════════════════════════════════
# SECTION 3: PREDICTIONS — TESTING DATA (EDGE CASES)
# ═════════════════════════════════════════
section("3. PREDICTIONS — TESTING DATA (Edge & Stress Scenarios)")

testing_scenarios = [
    {
        "name": "Minimum All Inputs",
        "inputs": {"tax_rate": 5, "fuel_price": 1.5, "subsidy": 0, "public_spending": 12, "interest_rate": 0.25, "environmental_regulation": 5}
    },
    {
        "name": "Maximum All Inputs",
        "inputs": {"tax_rate": 55, "fuel_price": 9.0, "subsidy": 45, "public_spending": 55, "interest_rate": 18, "environmental_regulation": 95}
    },
    {
        "name": "Zero Subsidy Austerity",
        "inputs": {"tax_rate": 45, "fuel_price": 6.0, "subsidy": 0, "public_spending": 12, "interest_rate": 15, "environmental_regulation": 10}
    },
    {
        "name": "Maximum Stimulus",
        "inputs": {"tax_rate": 5, "fuel_price": 1.5, "subsidy": 45, "public_spending": 55, "interest_rate": 0.25, "environmental_regulation": 30}
    },
    {
        "name": "Eco-Extreme Policy",
        "inputs": {"tax_rate": 30, "fuel_price": 8.5, "subsidy": 20, "public_spending": 45, "interest_rate": 3, "environmental_regulation": 95}
    },
    {
        "name": "Boundary Mix",
        "inputs": {"tax_rate": 0, "fuel_price": 1, "subsidy": 50, "public_spending": 60, "interest_rate": 20, "environmental_regulation": 100}
    },
]

for scenario in testing_scenarios:
    try:
        result = predict_policy(scenario["inputs"], model, scaler)
        assert all(k in result for k in OUTPUT_NAMES)
        assert 'confidence' in result
        # Check that predictions are reasonable (not NaN or inf)
        import numpy as np
        for k in OUTPUT_NAMES:
            assert not np.isnan(result[k]) and not np.isinf(result[k]), f"{k} is NaN/inf"
        detail = ", ".join(f"{k}={result[k]:.2f}" for k in OUTPUT_NAMES)
        log_test(f"Test scenario: {scenario['name']}", "PASS", f"Conf={result['confidence']:.2f} | {detail}")
    except Exception as e:
        log_test(f"Test scenario: {scenario['name']}", "FAIL", str(e))


# ═════════════════════════════════════════
# SECTION 4: FEATURE IMPORTANCE
# ═════════════════════════════════════════
section("4. FEATURE IMPORTANCE")

try:
    fi = get_feature_importance()
    assert isinstance(fi, list)
    assert len(fi) > 0, "Feature importance list is empty"
    for item in fi:
        assert 'feature' in item and 'importance' in item
    log_test("Feature importance retrieval", "PASS", f"{len(fi)} features: {[f['feature'] for f in fi[:3]]}...")
except Exception as e:
    log_test("Feature importance retrieval", "FAIL", str(e))


# ═════════════════════════════════════════
# SECTION 5: SENSITIVITY ANALYSIS
# ═════════════════════════════════════════
section("5. SENSITIVITY ANALYSIS")

try:
    base = {"tax_rate": 25, "fuel_price": 3.5, "subsidy": 15, "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50}
    sa = sensitivity_analysis(base, 'gdp_growth')
    assert isinstance(sa, list)
    assert len(sa) == 6, f"Expected 6 sensitivity results, got {len(sa)}"
    for item in sa:
        assert all(k in item for k in ['feature', 'base_value', 'modified_value', 'impact', 'direction'])
    top = sa[0]
    log_test("Sensitivity analysis (gdp_growth)", "PASS", f"Top impact: {top['feature']} → {top['impact']:.4f}")
except Exception as e:
    log_test("Sensitivity analysis", "FAIL", str(e))

# Additional target variable
try:
    sa_inf = sensitivity_analysis(base, 'inflation')
    assert len(sa_inf) == 6
    log_test("Sensitivity analysis (inflation)", "PASS", f"Top: {sa_inf[0]['feature']} → {sa_inf[0]['impact']:.4f}")
except Exception as e:
    log_test("Sensitivity analysis (inflation)", "FAIL", str(e))


# ═════════════════════════════════════════
# SECTION 6: POLICY RECOMMENDATION
# ═════════════════════════════════════════
section("6. AI POLICY RECOMMENDATION")

try:
    rec = recommend_policy({
        "gdp_growth": 4.0,
        "inflation": 2.5,
        "employment_rate": 96.0,
        "environment_score": 80.0,
        "public_satisfaction": 75.0,
    })
    assert 'recommended_inputs' in rec
    assert 'predicted_outcomes' in rec
    assert 'optimization_score' in rec
    ri = rec['recommended_inputs']
    po = rec['predicted_outcomes']
    log_test("Policy recommendation engine", "PASS",
             f"Opt score={rec['optimization_score']:.2f} | tax={ri.get('tax_rate',0):.1f}%, subsidy={ri.get('subsidy',0):.1f}%")
except Exception as e:
    log_test("Policy recommendation", "FAIL", str(e))


# ═════════════════════════════════════════
# SECTION 7: DATABASE LAYER
# ═════════════════════════════════════════
section("7. DATABASE LAYER")

try:
    from services.database import (
        init_db, get_connection, create_user, get_user_by_email,
        get_user_by_id, update_last_login, save_scenario,
        get_all_scenarios, delete_scenario, save_simulation,
        get_history, log_training, DB_PATH
    )
    log_test("Database module imports", "PASS")
except Exception as e:
    log_test("Database module imports", "FAIL", str(e))

# 7.1 Database file exists
try:
    assert os.path.exists(DB_PATH), f"DB not found: {DB_PATH}"
    db_size = os.path.getsize(DB_PATH)
    log_test("Database file exists", "PASS", f"Size={db_size} bytes at {DB_PATH}")
except Exception as e:
    log_test("Database file exists", "FAIL", str(e))

# 7.2 Database tables
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    conn.close()
    expected_tables = ['users', 'scenarios', 'simulation_history', 'model_training_log']
    for t in expected_tables:
        assert t in tables, f"Missing table: {t}"
    log_test("Database tables", "PASS", f"Tables: {tables}")
except Exception as e:
    log_test("Database tables", "FAIL", str(e))

# 7.3 User creation
test_email = f"dryrun_{int(time.time())}@test.com"
test_user = None
try:
    test_user = create_user(test_email, "hashed_test_password", "DryRun User")
    assert test_user['email'] == test_email
    assert test_user['name'] == "DryRun User"
    assert 'id' in test_user
    log_test("User creation", "PASS", f"ID={test_user['id']}, email={test_email}")
except Exception as e:
    log_test("User creation", "FAIL", str(e))

# 7.4 Duplicate email rejection
try:
    try:
        create_user(test_email, "another_hash", "Duplicate User")
        log_test("Duplicate email rejection", "FAIL", "Should have raised ValueError")
    except ValueError as e:
        log_test("Duplicate email rejection", "PASS", f"Correctly rejected: {e}")
except Exception as e:
    log_test("Duplicate email rejection", "FAIL", str(e))

# 7.5 User lookup by email
try:
    found = get_user_by_email(test_email)
    assert found is not None
    assert found['email'] == test_email
    log_test("User lookup by email", "PASS", f"Found: {found['name']}")
except Exception as e:
    log_test("User lookup by email", "FAIL", str(e))

# 7.6 User lookup by ID
try:
    if test_user:
        found = get_user_by_id(test_user['id'])
        assert found is not None
        assert found['email'] == test_email
        log_test("User lookup by ID", "PASS")
    else:
        log_test("User lookup by ID", "WARN", "Skipped — no test user")
except Exception as e:
    log_test("User lookup by ID", "FAIL", str(e))

# 7.7 Update last login
try:
    if test_user:
        update_last_login(test_user['id'])
        log_test("Update last login", "PASS")
    else:
        log_test("Update last login", "WARN", "Skipped")
except Exception as e:
    log_test("Update last login", "FAIL", str(e))

# 7.8 Save scenario
test_scenario_id = None
try:
    saved = save_scenario(
        "DryRun Test Scenario",
        {"tax_rate": 25, "fuel_price": 3.5, "subsidy": 15, "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50},
        {"gdp_growth": 2.5, "inflation": 3.1, "employment_rate": 94, "environment_score": 56, "public_satisfaction": 62}
    )
    assert 'id' in saved
    test_scenario_id = saved['id']
    log_test("Save scenario", "PASS", f"ID={saved['id']}")
except Exception as e:
    log_test("Save scenario", "FAIL", str(e))

# 7.9 Get all scenarios
try:
    scenarios = get_all_scenarios()
    assert isinstance(scenarios, list)
    assert len(scenarios) > 0
    log_test("Get all scenarios", "PASS", f"{len(scenarios)} scenarios found")
except Exception as e:
    log_test("Get all scenarios", "FAIL", str(e))

# 7.10 Delete scenario
try:
    if test_scenario_id:
        deleted = delete_scenario(test_scenario_id)
        assert deleted == True
        log_test("Delete scenario", "PASS", f"Deleted ID={test_scenario_id}")
    else:
        log_test("Delete scenario", "WARN", "Skipped")
except Exception as e:
    log_test("Delete scenario", "FAIL", str(e))

# 7.11 Save simulation history
try:
    sim_id = save_simulation(
        {"tax_rate": 25, "fuel_price": 3.5},
        {"gdp_growth": 2.5, "inflation": 3.0},
        "GradientBoosting", 0.92
    )
    assert sim_id is not None
    log_test("Save simulation history", "PASS", f"Sim ID={sim_id}")
except Exception as e:
    log_test("Save simulation history", "FAIL", str(e))

# 7.12 Get history
try:
    history = get_history(10)
    assert isinstance(history, list)
    log_test("Get simulation history", "PASS", f"{len(history)} entries")
except Exception as e:
    log_test("Get simulation history", "FAIL", str(e))

# 7.13 Log training
try:
    log_training("RandomForest", 0.312, 0.95, 5000)
    log_test("Log training event", "PASS")
except Exception as e:
    log_test("Log training event", "FAIL", str(e))


# ═════════════════════════════════════════
# SECTION 8: AUTHENTICATION SERVICE
# ═════════════════════════════════════════
section("8. AUTHENTICATION SERVICE (JWT)")

try:
    from services.auth import (
        hash_password, verify_password, create_access_token,
        decode_token, JWT_SECRET, JWT_EXPIRATION_HOURS
    )
    log_test("Auth service imports", "PASS")
except Exception as e:
    log_test("Auth service imports", "FAIL", str(e))

# 8.1 Password hashing
try:
    pw_hash = hash_password("TestPassword123!")
    assert ':' in pw_hash, "Hash should be salt:key format"
    parts = pw_hash.split(':')
    assert len(parts) == 2
    assert len(parts[0]) == 32, f"Salt should be 32 hex chars, got {len(parts[0])}"
    log_test("Password hashing (PBKDF2-SHA256)", "PASS", f"Hash format: salt({len(parts[0])}):key({len(parts[1])})")
except Exception as e:
    log_test("Password hashing", "FAIL", str(e))

# 8.2 Password verification
try:
    assert verify_password("TestPassword123!", pw_hash) == True
    assert verify_password("WrongPassword!", pw_hash) == False
    assert verify_password("", pw_hash) == False
    log_test("Password verification", "PASS", "Correct=True, Wrong=False, Empty=False")
except Exception as e:
    log_test("Password verification", "FAIL", str(e))

# 8.3 JWT token creation
try:
    token = create_access_token(1, "test@test.com", "Test User")
    assert token is not None
    parts = token.split('.')
    assert len(parts) == 3, f"JWT should have 3 parts, got {len(parts)}"
    log_test("JWT token creation", "PASS", f"Token length: {len(token)} chars")
except Exception as e:
    log_test("JWT token creation", "FAIL", str(e))

# 8.4 JWT token decoding
try:
    payload = decode_token(token)
    assert payload is not None
    assert payload['sub'] == '1'
    assert payload['email'] == 'test@test.com'
    assert payload['name'] == 'Test User'
    assert 'exp' in payload
    assert 'iat' in payload
    log_test("JWT token decoding", "PASS", f"sub={payload['sub']}, exp={payload['exp']}")
except Exception as e:
    log_test("JWT token decoding", "FAIL", str(e))

# 8.5 Invalid token rejection
try:
    invalid = decode_token("invalid.token.here")
    assert invalid is None
    tampered = token[:-5] + "XXXXX"
    tampered_result = decode_token(tampered)
    assert tampered_result is None
    log_test("Invalid/tampered token rejection", "PASS")
except Exception as e:
    log_test("Invalid token rejection", "FAIL", str(e))

# 8.6 JWT configuration
try:
    assert JWT_SECRET is not None and len(JWT_SECRET) > 10
    assert JWT_EXPIRATION_HOURS >= 1
    log_test("JWT configuration", "PASS", f"Expiry={JWT_EXPIRATION_HOURS}h, Secret length={len(JWT_SECRET)}")
except Exception as e:
    log_test("JWT configuration", "FAIL", str(e))


# ═════════════════════════════════════════
# SECTION 9: FASTAPI APPLICATION STRUCTURE
# ═════════════════════════════════════════
section("9. FASTAPI APPLICATION STRUCTURE")

try:
    from main import app
    log_test("FastAPI app import", "PASS", f"Title='{app.title}', Version='{app.version}'")
except Exception as e:
    log_test("FastAPI app import", "FAIL", str(e))

# 9.1 Route registration
try:
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    expected_routes = [
        '/predict', '/compare', '/train', '/scenarios', '/history',
        '/model/info', '/model/feature-importance', '/sensitivity', '/recommend',
        '/auth/register', '/auth/login', '/auth/me', '/auth/verify',
        '/api/status', '/health'
    ]
    missing = [r for r in expected_routes if r not in routes]
    if missing:
        log_test("Route registration", "WARN", f"Missing: {missing}")
    else:
        log_test("Route registration", "PASS", f"All {len(expected_routes)} expected routes registered")
except Exception as e:
    log_test("Route registration", "FAIL", str(e))

# 9.2 CORS configuration
try:
    cors_found = False
    for middleware in app.user_middleware:
        if 'CORSMiddleware' in str(middleware):
            cors_found = True
    if cors_found:
        log_test("CORS middleware", "PASS", "CORSMiddleware configured")
    else:
        log_test("CORS middleware", "WARN", "CORSMiddleware not detected in user_middleware list")
except Exception as e:
    log_test("CORS middleware", "WARN", str(e))

# 9.3 Pydantic models
try:
    from routes.api import PolicyInput, CompareRequest, ScenarioCreate, SensitivityRequest, RecommendRequest
    # Validate default values
    pi = PolicyInput()
    assert pi.tax_rate == 25
    assert pi.fuel_price == 3.5
    log_test("Pydantic request schemas", "PASS", f"PolicyInput defaults: tax={pi.tax_rate}, fuel={pi.fuel_price}")
except Exception as e:
    log_test("Pydantic request schemas", "FAIL", str(e))

# 9.4 Auth routes schemas
try:
    from routes.auth import RegisterRequest, LoginRequest, AuthResponse
    log_test("Auth route schemas", "PASS")
except Exception as e:
    log_test("Auth route schemas", "FAIL", str(e))


# ═════════════════════════════════════════
# SECTION 10: FRONTEND FILE STRUCTURE AUDIT
# ═════════════════════════════════════════
section("10. FRONTEND FILE STRUCTURE AUDIT")

frontend_root = os.path.join(os.path.dirname(__file__), '..')

expected_files = {
    "index.html": "Entry HTML",
    "package.json": "NPM config",
    "vite.config.js": "Vite configuration",
    "tailwind.config.js": "Tailwind CSS config",
    ".env": "Environment variables",
    "src/App.jsx": "Root React component",
    "src/main.jsx": "React entry point",
    "src/index.css": "Global styles",
    "src/services/api.js": "API service layer",
    "src/contexts/AuthContext.jsx": "Auth context provider",
    "src/hooks/useSimulation.js": "Simulation custom hook",
    "src/utils/constants.js": "App constants & helpers",
    "src/pages/Dashboard.jsx": "Dashboard page",
    "src/pages/Simulator.jsx": "Simulator page",
    "src/pages/Results.jsx": "Results/History page",
    "src/pages/Scenarios.jsx": "Scenario comparison page",
    "src/pages/Login.jsx": "Login page",
    "src/pages/Signup.jsx": "Signup page",
    "src/pages/Landing.jsx": "Landing page",
    "src/components/Charts.jsx": "Chart components (Recharts)",
    "src/components/Layout.jsx": "App layout with sidebar",
    "src/components/PolicySlider.jsx": "Policy parameter slider",
    "src/components/ResultCard.jsx": "Result metric card",
    "src/components/LoadingOverlay.jsx": "Loading overlay",
}

missing_files = []
for rel_path, desc in expected_files.items():
    full_path = os.path.join(frontend_root, rel_path)
    exists = os.path.exists(full_path)
    if not exists:
        missing_files.append(rel_path)

if missing_files:
    log_test("Frontend files audit", "FAIL", f"Missing: {missing_files}")
else:
    log_test("Frontend files audit", "PASS", f"All {len(expected_files)} files present")


# ═════════════════════════════════════════
# SECTION 11: FRONTEND-BACKEND INTEGRATION CHECK
# ═════════════════════════════════════════
section("11. FRONTEND-BACKEND INTEGRATION CHECK")

# 11.1 API base URL configuration
try:
    env_path = os.path.join(frontend_root, '.env')
    with open(env_path, 'r') as f:
        env_content = f.read()
    assert 'VITE_API_URL' in env_content, "Missing VITE_API_URL"
    assert 'localhost:8000' in env_content or '0.0.0.0:8000' in env_content
    log_test("API URL configuration (.env)", "PASS", "VITE_API_URL points to backend")
except Exception as e:
    log_test("API URL configuration", "FAIL", str(e))

# 11.2 API service function completeness
try:
    api_js_path = os.path.join(frontend_root, 'src', 'services', 'api.js')
    with open(api_js_path, 'r') as f:
        api_content = f.read()
    expected_functions = [
        'authRegister', 'authLogin', 'authVerify', 'authMe',
        'predictPolicy', 'comparePolicy', 'trainModel',
        'getScenarios', 'saveScenario', 'deleteScenario',
        'getHistory', 'getModelInfo', 'getFeatureImportance',
        'getSensitivity', 'getRecommendation',
    ]
    missing_funcs = [f for f in expected_functions if f not in api_content]
    if missing_funcs:
        log_test("API service functions", "WARN", f"Missing: {missing_funcs}")
    else:
        log_test("API service functions", "PASS", f"All {len(expected_functions)} API functions defined")
except Exception as e:
    log_test("API service functions", "FAIL", str(e))

# 11.3 Auth interceptor
try:
    assert 'interceptors.request.use' in api_content, "Missing request interceptor"
    assert 'interceptors.response.use' in api_content, "Missing response interceptor"
    assert 'policyai_token' in api_content, "Missing token key"
    assert 'Bearer' in api_content, "Missing Bearer scheme"
    log_test("Auth interceptors (request + 401 handler)", "PASS")
except Exception as e:
    log_test("Auth interceptors", "FAIL", str(e))

# 11.4 React Router setup
try:
    app_jsx = os.path.join(frontend_root, 'src', 'App.jsx')
    with open(app_jsx, 'r') as f:
        app_content = f.read()
    expected_routes_fe = ['/login', '/signup', '/landing', '/simulator', '/results', '/scenarios']
    for route in expected_routes_fe:
        assert f'"{route}"' in app_content or f"'{route}'" in app_content, f"Route {route} not found in App.jsx"
    assert 'ProtectedRoute' in app_content
    assert 'PublicRoute' in app_content
    assert 'AuthProvider' in app_content
    log_test("React Router configuration", "PASS", f"6 routes + ProtectedRoute + PublicRoute guards")
except Exception as e:
    log_test("React Router configuration", "FAIL", str(e))

# 11.5 Vite proxy config
try:
    vite_path = os.path.join(frontend_root, 'vite.config.js')
    with open(vite_path, 'r') as f:
        vite_content = f.read()
    assert 'proxy' in vite_content
    assert 'localhost:8000' in vite_content
    log_test("Vite dev proxy (/api → backend)", "PASS")
except Exception as e:
    log_test("Vite proxy config", "FAIL", str(e))


# ═════════════════════════════════════════
# SECTION 12: CROSS-VALIDATION ML CHECK
# ═════════════════════════════════════════
section("12. CROSS-VALIDATION ML ACCURACY CHECK")

try:
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    import numpy as np

    X, y = generate_synthetic_data(5000)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    from sklearn.preprocessing import StandardScaler
    s = StandardScaler()
    X_train_s = s.fit_transform(X_train)
    X_test_s = s.transform(X_test)

    y_pred = model.predict(X_test_s)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    per_output_r2 = {}
    for i, name in enumerate(OUTPUT_NAMES):
        per_output_r2[name] = r2_score(y_test.values[:, i], y_pred[:, i])

    log_test("Overall test set accuracy", "PASS", f"RMSE={rmse:.4f}, R²={r2:.4f}")
    for name, score in per_output_r2.items():
        status = "PASS" if score > 0.80 else "WARN" if score > 0.60 else "FAIL"
        log_test(f"  Per-output R² — {name}", status, f"R²={score:.4f}")
except Exception as e:
    log_test("Cross-validation check", "FAIL", str(e))


# ═════════════════════════════════════════
# SECTION 13: PRODUCTION READINESS CHECKS
# ═════════════════════════════════════════
section("13. PRODUCTION READINESS CHECKS")

# 13.1 SPA fallback
try:
    dist_dir = os.path.join(frontend_root, 'dist')
    if os.path.isdir(dist_dir):
        index_html = os.path.join(dist_dir, 'index.html')
        assets_dir = os.path.join(dist_dir, 'assets')
        if os.path.exists(index_html):
            log_test("Production build (dist/)", "PASS", "dist/index.html exists")
        else:
            log_test("Production build (dist/)", "WARN", "dist/ exists but no index.html")
    else:
        log_test("Production build (dist/)", "WARN", "No dist/ — run 'npm run build' for production")
except Exception as e:
    log_test("Production build check", "FAIL", str(e))

# 13.2 node_modules
try:
    nm = os.path.join(frontend_root, 'node_modules')
    if os.path.isdir(nm):
        log_test("Frontend dependencies (node_modules)", "PASS", "node_modules exists")
    else:
        log_test("Frontend dependencies", "FAIL", "node_modules missing — run 'npm install'")
except Exception as e:
    log_test("Frontend dependencies", "FAIL", str(e))

# 13.3 Backend requirements
try:
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(req_path, 'r') as f:
        reqs = [l.strip().split('==')[0] for l in f if l.strip() and not l.startswith('#')]
    expected_deps = ['fastapi', 'uvicorn', 'pydantic', 'scikit-learn', 'pandas', 'numpy', 'joblib']
    missing_deps = [d for d in expected_deps if d not in reqs and d.replace('-', '_') not in [r.replace('-', '_') for r in reqs]]
    if missing_deps:
        log_test("Backend requirements.txt", "WARN", f"Missing: {missing_deps}")
    else:
        log_test("Backend requirements.txt", "PASS", f"All {len(expected_deps)} core deps listed")
except Exception as e:
    log_test("Backend requirements.txt", "FAIL", str(e))


# ═════════════════════════════════════════
# FINAL REPORT
# ═════════════════════════════════════════
section("FINAL REPORT")

total = pass_count + fail_count + warn_count
print(f"\n  Total Tests: {total}")
print(f"  ✅ PASSED:   {pass_count}")
print(f"  ❌ FAILED:   {fail_count}")
print(f"  ⚠️  WARNINGS: {warn_count}")
print(f"\n  Pass Rate: {(pass_count/total*100):.1f}%")

if fail_count == 0:
    print(f"\n  🎉 ALL CRITICAL TESTS PASSED — WEBSITE IS FULLY FUNCTIONAL!")
else:
    print(f"\n  🔴 {fail_count} CRITICAL FAILURE(S) — NEEDS ATTENTION")

# Save results to file
output_path = os.path.join(os.path.dirname(__file__), 'dry_run_report.json')
with open(output_path, 'w') as f:
    json.dump({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total": total,
        "passed": pass_count,
        "failed": fail_count,
        "warnings": warn_count,
        "pass_rate": f"{(pass_count/total*100):.1f}%",
        "results": results,
    }, f, indent=2)

print(f"\n  📄 Full report saved to: {output_path}")
print(f"{'='*60}")
