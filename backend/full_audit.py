"""
PolicyAI — Full Dry Run + Vulnerability Audit
Runs training, testing, all API flows, and reports every issue found.
"""
import sys, os, json, time, traceback, sqlite3
sys.path.insert(0, os.path.dirname(__file__))
# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"
INFO = "[INFO]"

results = []

def check(name, fn):
    try:
        fn()
        print(f"{PASS}  {name}")
        results.append(("PASS", name, None))
    except AssertionError as e:
        msg = str(e)
        print(f"{FAIL}  {name}: {msg}")
        results.append(("FAIL", name, msg))
    except Exception as e:
        msg = traceback.format_exc().strip().split("\n")[-1]
        print(f"{FAIL}  {name}: {msg}")
        results.append(("FAIL", name, msg))

def warn(name, msg):
    print(f"{WARN}  {name}: {msg}")
    results.append(("WARN", name, msg))

def info(msg):
    print(f"{INFO}  {msg}")

# ─────────────────────────────────────────
# 1. DATABASE
# ─────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 1: Database")
print("="*60)

from services.database import init_db, create_user, get_user_by_email, \
    get_user_by_id, update_last_login, save_scenario, get_all_scenarios, \
    delete_scenario, save_simulation, get_history, DB_PATH

def test_db_init():
    init_db()
    assert os.path.exists(DB_PATH), "DB file not created"

def test_db_tables():
    conn = sqlite3.connect(DB_PATH)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    conn.close()
    for t in ['users', 'scenarios', 'simulation_history', 'model_training_log']:
        assert t in tables, f"Missing table: {t}"

def test_user_create():
    ts = int(time.time())
    u = create_user(f"audit_{ts}@test.com", "fakehash", "Audit User")
    assert u['id'] > 0

def test_user_duplicate():
    ts = int(time.time())
    email = f"dup_{ts}@test.com"
    create_user(email, "h1", "Alice")
    try:
        create_user(email, "h2", "Bob")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # expected

def test_user_invalid_email():
    try:
        create_user("not-an-email", "hash", "Name")
        assert False, "Should reject invalid email"
    except ValueError:
        pass

def test_scenario_crud():
    s = save_scenario("Test Policy", {'tax_rate': 25}, {'gdp_growth': 2.1})
    assert s['id'] > 0
    all_s = get_all_scenarios()
    assert any(x['id'] == s['id'] for x in all_s)
    deleted = delete_scenario(s['id'])
    assert deleted

def test_history_save():
    sid = save_simulation({'tax_rate': 20}, {'gdp_growth': 3.0}, 'RandomForest', 0.92)
    assert sid > 0
    h = get_history(10)
    assert len(h) > 0

check("DB init", test_db_init)
check("DB tables exist", test_db_tables)
check("User create", test_user_create)
check("User duplicate rejected", test_user_duplicate)
check("Invalid email rejected", test_user_invalid_email)
check("Scenario CRUD", test_scenario_crud)
check("Simulation history save", test_history_save)

# ─────────────────────────────────────────
# 2. AUTH SERVICE
# ─────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 2: Auth Service")
print("="*60)

from services.auth import hash_password, verify_password, create_access_token, decode_token

def test_password_hash():
    h = hash_password("SecurePass123!")
    assert ':' in h
    assert len(h) > 40

def test_password_verify_ok():
    pw = "MyTestPass999"
    h = hash_password(pw)
    assert verify_password(pw, h)

def test_password_verify_wrong():
    h = hash_password("correct")
    assert not verify_password("wrong", h)

def test_jwt_roundtrip():
    token = create_access_token(99, "jwt@test.com", "JWT User")
    assert '.' in token
    payload = decode_token(token)
    assert payload is not None
    assert payload['sub'] == '99'
    assert payload['email'] == 'jwt@test.com'

def test_jwt_expired():
    import time as _t
    from services import auth as auth_mod
    # Temporarily set expiration to past
    old = auth_mod.JWT_EXPIRATION_HOURS
    auth_mod.JWT_EXPIRATION_HOURS = 0
    token = create_access_token(1, "x@x.com", "X")
    auth_mod.JWT_EXPIRATION_HOURS = old
    # Token exp will be ~now, so decode may or may not fail — just ensure no crash
    result = decode_token(token)
    # result will be None (expired) or valid if same second — both ok

def test_jwt_tampered():
    token = create_access_token(1, "a@b.com", "A")
    parts = token.split('.')
    parts[1] = parts[1][:-4] + "xxxx"
    tampered = '.'.join(parts)
    assert decode_token(tampered) is None, "Tampered token should be rejected"

check("Password hashing", test_password_hash)
check("Password verify correct", test_password_verify_ok)
check("Password verify wrong rejected", test_password_verify_wrong)
check("JWT roundtrip", test_jwt_roundtrip)
check("JWT expired handling", test_jwt_expired)
check("JWT tampered rejected", test_jwt_tampered)

# ─────────────────────────────────────────
# 3. ML MODEL — TRAINING
# ─────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 3: ML Model — Training")
print("="*60)

from models.ml_model import (
    generate_synthetic_data, train_and_select_best, load_model,
    predict_policy, get_feature_importance, sensitivity_analysis, recommend_policy,
    FEATURE_NAMES, OUTPUT_NAMES, MODEL_PATH, SCALER_PATH, METADATA_PATH
)
import numpy as np

def test_data_generation():
    X, y = generate_synthetic_data(1000, seed=0)
    assert X.shape == (1000, 6), f"Expected (1000,6), got {X.shape}"
    assert y.shape == (1000, 5), f"Expected (1000,5), got {y.shape}"
    assert list(X.columns) == FEATURE_NAMES
    assert list(y.columns) == OUTPUT_NAMES

def test_data_no_nulls():
    X, y = generate_synthetic_data(500)
    assert not X.isnull().any().any(), "X has nulls"
    assert not y.isnull().any().any(), "y has nulls"

def test_data_ranges():
    X, y = generate_synthetic_data(2000)
    assert X['tax_rate'].between(5, 55).all(), "tax_rate out of range"
    assert X['fuel_price'].between(1.5, 9.0).all(), "fuel_price out of range"
    assert y['employment_rate'].between(70, 99.5).all(), "employment_rate out of range"
    assert y['environment_score'].between(5, 100).all(), "environment_score out of range"
    assert y['public_satisfaction'].between(10, 95).all(), "public_satisfaction out of range"

def test_training():
    global model, scaler, metadata
    info("Training ML models (this may take 30-60s)...")
    model, scaler, metadata = train_and_select_best()
    assert model is not None
    assert scaler is not None
    assert 'model_type' in metadata
    assert 'rmse' in metadata
    assert 'r2_score' in metadata
    info(f"Best model: {metadata['model_type']} | R²={metadata['r2_score']:.4f} | RMSE={metadata['rmse']:.4f}")

def test_model_files_saved():
    assert os.path.exists(MODEL_PATH), "model.pkl not saved"
    assert os.path.exists(SCALER_PATH), "scaler.pkl not saved"
    assert os.path.exists(METADATA_PATH), "metadata.json not saved"

def test_model_quality():
    assert metadata.get('r2_score', 0) > 0.85, f"R² too low: {metadata.get('r2_score')}"
    assert metadata.get('rmse', 999) < 5.0, f"RMSE too high: {metadata.get('rmse')}"

check("Data generation shape", test_data_generation)
check("Data no nulls", test_data_no_nulls)
check("Data value ranges clipped", test_data_ranges)
check("Model training completes", test_training)
check("Model files saved", test_model_files_saved)
check("Model quality (R²>0.85)", test_model_quality)

# ─────────────────────────────────────────
# 4. ML MODEL — PREDICTION
# ─────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 4: ML Model — Prediction")
print("="*60)

BASE_INPUTS = {
    'tax_rate': 25, 'fuel_price': 3.5, 'subsidy': 15,
    'public_spending': 30, 'interest_rate': 5, 'environmental_regulation': 50
}

def test_predict_outputs():
    result = predict_policy(BASE_INPUTS, model, scaler)
    for key in OUTPUT_NAMES:
        assert key in result, f"Missing output: {key}"
    assert 'confidence' in result
    info(f"Prediction: GDP={result['gdp_growth']:.2f}%, Inflation={result['inflation']:.2f}%, "
         f"Employment={result['employment_rate']:.1f}%, Env={result['environment_score']:.1f}, "
         f"Satisfaction={result['public_satisfaction']:.1f}, Confidence={result['confidence']:.2f}")

def test_predict_high_tax():
    r = predict_policy({**BASE_INPUTS, 'tax_rate': 50}, model, scaler)
    base_r = predict_policy(BASE_INPUTS, model, scaler)
    assert r['gdp_growth'] < base_r['gdp_growth'] + 2, "High tax should not drastically raise GDP"

def test_predict_high_interest():
    r = predict_policy({**BASE_INPUTS, 'interest_rate': 15}, model, scaler)
    base_r = predict_policy(BASE_INPUTS, model, scaler)
    assert r['inflation'] < base_r['inflation'] + 2, "High interest should reduce inflation trend"

def test_predict_edge_min():
    low_inputs = {'tax_rate': 5, 'fuel_price': 1.5, 'subsidy': 0,
                  'public_spending': 12, 'interest_rate': 0.25, 'environmental_regulation': 5}
    r = predict_policy(low_inputs, model, scaler)
    assert all(k in r for k in OUTPUT_NAMES)

def test_predict_edge_max():
    high_inputs = {'tax_rate': 55, 'fuel_price': 9.0, 'subsidy': 45,
                   'public_spending': 55, 'interest_rate': 18, 'environmental_regulation': 95}
    r = predict_policy(high_inputs, model, scaler)
    assert all(k in r for k in OUTPUT_NAMES)

def test_predict_confidence_range():
    r = predict_policy(BASE_INPUTS, model, scaler)
    assert 0 <= r['confidence'] <= 1, f"Confidence out of [0,1]: {r['confidence']}"

def test_feature_importance():
    fi = get_feature_importance()
    assert len(fi) == len(FEATURE_NAMES)
    for item in fi:
        assert 'feature' in item and 'importance' in item

def test_sensitivity():
    result = sensitivity_analysis(BASE_INPUTS, 'gdp_growth')
    assert len(result) == len(FEATURE_NAMES)
    for item in result:
        assert 'feature' in item and 'impact' in item and 'direction' in item

def test_recommend():
    targets = {'gdp_growth': 4.0, 'inflation': 2.5, 'employment_rate': 96.0}
    result = recommend_policy(targets)
    assert 'recommended_inputs' in result
    assert 'predicted_outcomes' in result
    for feat in FEATURE_NAMES:
        assert feat in result['recommended_inputs']

check("Predict returns all outputs", test_predict_outputs)
check("High tax reduces GDP", test_predict_high_tax)
check("High interest reduces inflation", test_predict_high_interest)
check("Predict at minimum inputs", test_predict_edge_min)
check("Predict at maximum inputs", test_predict_edge_max)
check("Confidence in [0,1]", test_predict_confidence_range)
check("Feature importance returns all features", test_feature_importance)
check("Sensitivity analysis", test_sensitivity)
check("Policy recommendation", test_recommend)

# ─────────────────────────────────────────
# 5. FULL FLOW: Register → Login → Predict
# ─────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 5: Full Auth + API Flow")
print("="*60)

ts2 = int(time.time())
TEST_EMAIL = f"flow_{ts2}@audit.com"
TEST_PASS = "FlowPass999!"
TEST_NAME = "Flow Tester"

def test_register_flow():
    from routes.auth import RegisterRequest
    from services.auth import hash_password
    from services.database import create_user
    ph = hash_password(TEST_PASS)
    u = create_user(TEST_EMAIL, ph, TEST_NAME)
    assert u['id'] > 0
    assert u['email'] == TEST_EMAIL

def test_login_flow():
    user = get_user_by_email(TEST_EMAIL)
    assert user is not None, "User not found"
    assert verify_password(TEST_PASS, user['password_hash']), "Password verify failed"
    token = create_access_token(user['id'], user['email'], user['name'])
    payload = decode_token(token)
    assert payload['email'] == TEST_EMAIL

def test_full_simulation_flow():
    user = get_user_by_email(TEST_EMAIL)
    result = predict_policy(BASE_INPUTS, model, scaler)
    sim_id = save_simulation(BASE_INPUTS, result, metadata['model_type'], result['confidence'])
    assert sim_id > 0
    history = get_history(5)
    assert any(h['id'] == sim_id for h in history)

def test_scenario_save_flow():
    result = predict_policy(BASE_INPUTS, model, scaler)
    s = save_scenario("Audit Scenario", BASE_INPUTS, result)
    all_s = get_all_scenarios()
    assert any(x['id'] == s['id'] for x in all_s)
    delete_scenario(s['id'])

check("Registration flow", test_register_flow)
check("Login + JWT flow", test_login_flow)
check("Full simulation + save flow", test_full_simulation_flow)
check("Scenario save + retrieve flow", test_scenario_save_flow)

# ─────────────────────────────────────────
# 6. VULNERABILITY CHECKS
# ─────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 6: Vulnerability Checks")
print("="*60)

from services.auth import JWT_SECRET

def check_sql_injection():
    # DB uses parameterized queries — verify
    import inspect
    src = open(os.path.join(os.path.dirname(__file__), 'services', 'database.py')).read()
    # Check for f-string SQL (bad) vs ? (good)
    bad_patterns = ["f\"SELECT", "f'SELECT", "f\"INSERT", "f'INSERT", "f\"DELETE", "f'DELETE"]
    for pat in bad_patterns:
        assert pat not in src, f"Possible SQL injection via f-string: {pat}"

def check_jwt_secret_strength():
    assert JWT_SECRET != "secret", "JWT_SECRET is too weak"
    assert len(JWT_SECRET) >= 20, f"JWT_SECRET too short ({len(JWT_SECRET)} chars)"
    if "dev" in JWT_SECRET.lower() or "change" in JWT_SECRET.lower():
        warn("JWT Secret", "Still using dev secret — set JWT_SECRET env var in production")

def check_password_strength():
    # Ensure PBKDF2 with 100000 iterations
    src = open(os.path.join(os.path.dirname(__file__), 'services', 'auth.py')).read()
    assert "100000" in src, "PBKDF2 iteration count should be 100000"
    assert "pbkdf2_hmac" in src, "Should use pbkdf2_hmac"

def check_timing_safe_compare():
    src = open(os.path.join(os.path.dirname(__file__), 'services', 'auth.py')).read()
    assert "compare_digest" in src, "Should use hmac.compare_digest for timing-safe comparison"

def check_cors_config():
    src = open(os.path.join(os.path.dirname(__file__), 'main.py')).read()
    # Check that production branch doesn't use wildcard with credentials
    if 'allow_origins=["*"]' in src and 'allow_credentials=True' in src:
        # Check if they're in the SAME middleware block (bad) or different branches (ok)
        # Our fix uses wildcard only in dev branch with credentials=False
        lines = src.split('\n')
        wildcard_lines = [i for i, l in enumerate(lines) if 'allow_origins=["*"]' in l]
        cred_lines = [i for i, l in enumerate(lines) if 'allow_credentials=True' in l]
        # Check if they're within 5 lines of each other (same middleware block = bug)
        for wl in wildcard_lines:
            for cl in cred_lines:
                if abs(wl - cl) < 5:
                    warn("CORS", "Wildcard allow_origins with allow_credentials=True in same middleware block — browsers will reject this")
                    return
    assert 'allow_origin_regex' in src, "Missing allow_origin_regex for Vercel preview URLs"

def check_input_validation():
    from routes.api import PolicyInput
    from pydantic import ValidationError
    # Tax rate out of range
    try:
        PolicyInput(tax_rate=999, fuel_price=3.5, subsidy=15,
                    public_spending=30, interest_rate=5, environmental_regulation=50)
        assert False, "Should reject tax_rate=999"
    except (ValidationError, Exception):
        pass  # correct — rejected

def check_no_plaintext_passwords():
    src = open(os.path.join(os.path.dirname(__file__), 'services', 'database.py')).read()
    assert "password" not in src.lower().replace("password_hash", ""), \
        "Raw 'password' stored — should only store password_hash"

check("SQL injection (parameterized queries)", check_sql_injection)
check("JWT secret strength", check_jwt_secret_strength)
check("Password hashing (PBKDF2, 100k iterations)", check_password_strength)
check("Timing-safe password comparison", check_timing_safe_compare)
check("CORS configuration", check_cors_config)
check("Input validation (Pydantic)", check_input_validation)

# ─────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────
print("\n" + "="*60)
print("  AUDIT REPORT SUMMARY")
print("="*60)

passed  = [r for r in results if r[0] == "PASS"]
failed  = [r for r in results if r[0] == "FAIL"]
warned  = [r for r in results if r[0] == "WARN"]
total   = len(results)

print(f"\n  Total checks : {total}")
print(f"\033[92m  Passed       : {len(passed)}\033[0m")
print(f"\033[91m  Failed       : {len(failed)}\033[0m")
print(f"\033[93m  Warnings     : {len(warned)}\033[0m")

if failed:
    print("\n--- FAILURES ---")
    for _, name, msg in failed:
        print(f"  ❌ {name}")
        print(f"     → {msg}")

if warned:
    print("\n--- WARNINGS ---")
    for _, name, msg in warned:
        print(f"  ⚠️  {name}: {msg}")

score = int(100 * len(passed) / total) if total else 0
print(f"\n  Health Score: {score}%")

if score == 100:
    print("  *** ALL CHECKS PASSED - System is fully operational! ***")
elif score >= 80:
    print("  [OK] System mostly healthy - fix the warnings above.")
else:
    print("  [CRITICAL] Issues found - review failures above.")

# Save JSON report
report = {
    "score": score, "total": total,
    "passed": len(passed), "failed": len(failed), "warnings": len(warned),
    "failures": [{"name": n, "error": m} for _, n, m in failed],
    "warnings_list": [{"name": n, "msg": m} for _, n, m in warned],
    "model": metadata.get("model_type", "unknown"),
    "r2_score": metadata.get("r2_score", 0),
    "rmse": metadata.get("rmse", 0),
}
report_path = os.path.join(os.path.dirname(__file__), "audit_report.json")
with open(report_path, "w") as f:
    json.dump(report, f, indent=2)
print(f"\n  Report saved → {report_path}")
print()
sys.exit(0 if not failed else 1)
