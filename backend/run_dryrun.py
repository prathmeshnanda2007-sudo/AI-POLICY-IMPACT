"""
AI Policy Impact Simulator -- Full Dry Run Test
Runs standalone (no HTTP server needed) to validate every layer.
"""
import sys
import os
import json
import time
import traceback
from datetime import datetime

# Force UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ---- Path Setup ----
sys.path.insert(0, os.path.dirname(__file__))

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"

results = []

def test(name, fn):
    start = time.time()
    try:
        out = fn()
        elapsed = (time.time() - start) * 1000
        results.append({"name": name, "status": "PASS", "ms": round(elapsed, 1), "detail": str(out)[:120]})
        print(f"{PASS}  [{elapsed:7.1f}ms]  {name}")
        if out:
            print(f"           -> {str(out)[:100]}")
        return out
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        results.append({"name": name, "status": "FAIL", "ms": round(elapsed, 1), "detail": str(e)})
        print(f"{FAIL}  [{elapsed:7.1f}ms]  {name}")
        print(f"           -> {e}")
        traceback.print_exc()
        return None


print("=" * 65)
print("  AI POLICY IMPACT SIMULATOR -- FULL DRY RUN")
print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 65)

# ================================================================
# LAYER 1: DATABASE
# ================================================================
print("\n[LAYER 1] DATABASE\n")

def test_db_init():
    from services.database import init_db
    init_db()
    return "DB initialized"

def test_create_user():
    from services.database import create_user, get_user_by_email
    import random
    email = f"dryrun_{random.randint(1000,9999)}@test.com"
    user = create_user(email=email, password_hash="fakehash:abc123", name="Dry Run User")
    assert user["id"] > 0
    assert user["email"] == email
    fetched = get_user_by_email(email)
    assert fetched is not None
    return f"user_id={user['id']}, email={email}"

def test_save_scenario():
    from services.database import save_scenario, get_all_scenarios
    s = save_scenario("Test Scenario", {"tax_rate": 30}, {"gdp_growth": 2.5})
    assert s["id"] > 0
    all_s = get_all_scenarios()
    assert len(all_s) >= 1
    return f"scenario_id={s['id']}, total={len(all_s)}"

def test_save_simulation():
    from services.database import save_simulation, get_history
    sid = save_simulation(
        inputs={"tax_rate": 25, "fuel_price": 3.5},
        results={"gdp_growth": 2.1, "inflation": 3.2},
        model_type="RandomForest",
        confidence=0.91
    )
    assert sid > 0
    history = get_history(10)
    assert len(history) >= 1
    return f"sim_id={sid}, history_count={len(history)}"

test("DB Init", test_db_init)
test("Create User + Lookup", test_create_user)
test("Save + Fetch Scenario", test_save_scenario)
test("Save + Fetch Simulation History", test_save_simulation)


# ================================================================
# LAYER 2: AUTH SERVICE
# ================================================================
print("\n[LAYER 2] AUTH SERVICE\n")

def test_password_hash():
    from services.auth import hash_password, verify_password
    pw = "SecurePass123!"
    hashed = hash_password(pw)
    assert ":" in hashed
    assert verify_password(pw, hashed)
    assert not verify_password("WrongPass", hashed)
    return f"hash={hashed[:30]}..."

def test_jwt_create_decode():
    from services.auth import create_access_token, decode_token
    token = create_access_token(user_id=1, email="test@test.com", name="Tester")
    assert token.count(".") == 2
    payload = decode_token(token)
    assert payload is not None
    assert payload["email"] == "test@test.com"
    assert payload["sub"] == "1"
    return f"token={token[:40]}..."

def test_jwt_expiry():
    from services.auth import decode_token
    import json, base64, hmac, hashlib, os
    secret = os.environ.get("JWT_SECRET", "policyai_dev_secret_key_change_in_production_2026")
    def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
    header = b64e(json.dumps({"alg":"HS256","typ":"JWT"}).encode())
    payload_data = {"sub":"1","email":"x@x.com","name":"X","iat":0,"exp":1}  # expired
    payload = b64e(json.dumps(payload_data).encode())
    msg = f"{header}.{payload}"
    sig = b64e(hmac.new(secret.encode(), msg.encode(), hashlib.sha256).digest())
    expired_token = f"{msg}.{sig}"
    result = decode_token(expired_token)
    assert result is None, "Expired token should return None"
    return "Expired token correctly rejected"

test("Password Hash & Verify", test_password_hash)
test("JWT Create & Decode", test_jwt_create_decode)
test("JWT Expiry Rejection", test_jwt_expiry)


# ================================================================
# LAYER 3: ML PIPELINE -- TRAINING DATA
# ================================================================
print("\n[LAYER 3] ML PIPELINE (Training Data)\n")

def test_generate_data():
    from models.ml_model import generate_synthetic_data
    X, y = generate_synthetic_data(n_samples=500, seed=42)
    assert len(X) == 500
    assert list(X.columns) == ['tax_rate', 'fuel_price', 'subsidy', 'public_spending', 'interest_rate', 'environmental_regulation']
    assert list(y.columns) == ['gdp_growth', 'inflation', 'employment_rate', 'environment_score', 'public_satisfaction']
    return f"X.shape={X.shape}, y.shape={y.shape}"

def test_model_training():
    from models.ml_model import train_and_select_best
    print(f"\n           Training 3 models on 5000 samples (may take ~30s)...")
    m, s, meta = train_and_select_best()
    assert meta["model_type"] in ["RandomForest", "GradientBoosting", "LinearRegression"]
    assert meta["r2_score"] > 0.85, f"R2 too low: {meta['r2_score']}"
    assert meta["rmse"] < 5.0
    return f"Best={meta['model_type']} | R2={meta['r2_score']:.4f} | RMSE={meta['rmse']:.4f}"

def test_model_load():
    from models.ml_model import load_model
    m, s, meta = load_model()
    assert m is not None
    assert s is not None
    return f"Loaded {meta.get('model_type')} from disk"

test("Generate Synthetic Data (500 samples)", test_generate_data)
test("Train & Select Best Model (5000 samples)", test_model_training)
test("Load Saved Model", test_model_load)


# ================================================================
# LAYER 4: PREDICTIONS -- TRAINING & TESTING DATA
# ================================================================
print("\n[LAYER 4] PREDICTIONS (Training & Testing Scenarios)\n")

TRAINING_SCENARIOS = [
    {"name": "High Tax + Green",  "tax_rate": 45, "fuel_price": 6.0, "subsidy": 10, "public_spending": 40, "interest_rate": 3,  "environmental_regulation": 85},
    {"name": "Low Tax + Stimulus","tax_rate": 10, "fuel_price": 2.0, "subsidy": 35, "public_spending": 20, "interest_rate": 2,  "environmental_regulation": 30},
    {"name": "Balanced Default",  "tax_rate": 25, "fuel_price": 3.5, "subsidy": 15, "public_spending": 30, "interest_rate": 5,  "environmental_regulation": 50},
    {"name": "Austerity",         "tax_rate": 35, "fuel_price": 4.0, "subsidy": 5,  "public_spending": 15, "interest_rate": 8,  "environmental_regulation": 40},
    {"name": "Expansionary",      "tax_rate": 20, "fuel_price": 3.0, "subsidy": 40, "public_spending": 55, "interest_rate": 1,  "environmental_regulation": 60},
]

TESTING_SCENARIOS = [
    {"name": "Edge: Max Tax",    "tax_rate": 60, "fuel_price": 10.0, "subsidy": 0,  "public_spending": 10, "interest_rate": 20, "environmental_regulation": 0},
    {"name": "Edge: Min Tax",    "tax_rate": 0,  "fuel_price": 1.0,  "subsidy": 50, "public_spending": 60, "interest_rate": 0,  "environmental_regulation": 100},
    {"name": "Climate Focus",    "tax_rate": 30, "fuel_price": 8.0,  "subsidy": 25, "public_spending": 45, "interest_rate": 4,  "environmental_regulation": 95},
    {"name": "Economic Growth",  "tax_rate": 15, "fuel_price": 2.5,  "subsidy": 30, "public_spending": 35, "interest_rate": 2,  "environmental_regulation": 25},
    {"name": "Stagflation Risk", "tax_rate": 50, "fuel_price": 7.5,  "subsidy": 5,  "public_spending": 50, "interest_rate": 15, "environmental_regulation": 20},
]

def run_scenario_predictions(label, scenarios):
    from models.ml_model import load_model, predict_policy
    m, s, meta = load_model()
    all_results = []
    for sc in scenarios:
        inputs = {k: v for k, v in sc.items() if k != "name"}
        result = predict_policy(inputs, m, s)
        all_results.append(result)
        assert "gdp_growth" in result
        assert "inflation" in result
        assert "employment_rate" in result
        assert "environment_score" in result
        assert "public_satisfaction" in result
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0
    print(f"\n           [{label}] Results:")
    print(f"           {'Scenario':<22} {'GDP%':>6} {'Inf%':>6} {'Emp%':>6} {'Env':>6} {'Sat%':>6} {'Conf':>6}")
    print(f"           {'-'*62}")
    for sc, r in zip(scenarios, all_results):
        print(f"           {sc['name']:<22} {r['gdp_growth']:>6.2f} {r['inflation']:>6.2f} {r['employment_rate']:>6.2f} {r['environment_score']:>6.2f} {r['public_satisfaction']:>6.2f} {r['confidence']:>6.2f}")
    return f"{len(scenarios)} scenarios predicted successfully"

test(f"Training Data Predictions ({len(TRAINING_SCENARIOS)} scenarios)", lambda: run_scenario_predictions("TRAIN", TRAINING_SCENARIOS))
test(f"Testing Data Predictions ({len(TESTING_SCENARIOS)} scenarios)", lambda: run_scenario_predictions("TEST", TESTING_SCENARIOS))


# ================================================================
# LAYER 5: ADVANCED ML FEATURES
# ================================================================
print("\n[LAYER 5] ADVANCED ML FEATURES\n")

def test_feature_importance():
    from models.ml_model import get_feature_importance
    fi = get_feature_importance()
    assert len(fi) > 0
    assert "feature" in fi[0] and "importance" in fi[0]
    top = fi[0]
    return f"Top feature: {top['feature']} (importance={top['importance']})"

def test_sensitivity_analysis():
    from models.ml_model import sensitivity_analysis
    base = {"tax_rate": 25, "fuel_price": 3.5, "subsidy": 15, "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50}
    result = sensitivity_analysis(base, "gdp_growth")
    assert len(result) == 6
    for r in result:
        assert "feature" in r
        assert "impact" in r
    top = result[0]
    return f"Most sensitive: {top['feature']} (impact={top['impact']:+.4f})"

def test_policy_recommendation():
    from models.ml_model import recommend_policy
    targets = {"gdp_growth": 4.0, "inflation": 2.5, "employment_rate": 96, "environment_score": 80}
    result = recommend_policy(targets)
    assert "recommended_inputs" in result
    assert "predicted_outcomes" in result
    inp = result["recommended_inputs"]
    assert 0 <= inp["tax_rate"] <= 60
    return f"Recommended tax_rate={inp['tax_rate']:.1f}%, fuel={inp['fuel_price']:.1f}"

test("Feature Importance", test_feature_importance)
test("Sensitivity Analysis (GDP)", test_sensitivity_analysis)
test("Policy Recommendation (Optimization)", test_policy_recommendation)


# ================================================================
# LAYER 6: END-TO-END FLOW
# ================================================================
print("\n[LAYER 6] END-TO-END FLOW\n")

def test_full_e2e_flow():
    import random
    from services.auth import hash_password, create_access_token, decode_token
    from services.database import create_user, save_simulation, save_scenario, get_history, log_training
    from models.ml_model import load_model, predict_policy

    # 1. Register user
    email = f"e2e_{random.randint(10000, 99999)}@policyai.test"
    pw_hash = hash_password("TestPass2026!")
    user = create_user(email=email, password_hash=pw_hash, name="E2E Tester")

    # 2. Create JWT
    token = create_access_token(user["id"], user["email"], user["name"])
    payload = decode_token(token)
    assert payload["email"] == email

    # 3. Run prediction
    m, s, meta = load_model()
    inputs = {"tax_rate": 28, "fuel_price": 4.0, "subsidy": 18, "public_spending": 32, "interest_rate": 4.5, "environmental_regulation": 65}
    result = predict_policy(inputs, m, s)

    # 4. Save simulation to DB
    sim_id = save_simulation(inputs=inputs, results=result, model_type=meta.get("model_type"), confidence=result["confidence"])

    # 5. Save as named scenario
    scenario = save_scenario("E2E Test Scenario", inputs, result)

    # 6. Log training
    log_training(meta["model_type"], meta["rmse"], meta["r2_score"], meta["training_samples"])

    # 7. Fetch history
    history = get_history(5)
    assert any(h["id"] == sim_id for h in history)

    return f"user_id={user['id']}, sim_id={sim_id}, scenario_id={scenario['id']}, gdp={result['gdp_growth']:.2f}%"

test("Full E2E Flow (Register -> Auth -> Predict -> Save -> History)", test_full_e2e_flow)


# ================================================================
# SUMMARY REPORT
# ================================================================
print("\n" + "=" * 65)
print("  DRY RUN SUMMARY REPORT")
print("=" * 65)

passed = [r for r in results if r["status"] == "PASS"]
failed = [r for r in results if r["status"] == "FAIL"]

print(f"\n  Total Tests : {len(results)}")
print(f"  {PASS}  Passed : {len(passed)}")
print(f"  {FAIL}  Failed : {len(failed)}")

if failed:
    print(f"\n  FAILED TESTS:")
    for r in failed:
        print(f"     x {r['name']}: {r['detail'][:80]}")

status_label = "ALL SYSTEMS GO - PRODUCTION READY" if not failed else "ISSUES FOUND -- SEE ABOVE"
print(f"\n  Overall Status: [{status_label}]")
print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 65 + "\n")

# Save JSON report
report_path = os.path.join(os.path.dirname(__file__), "dry_run_final.json")
with open(report_path, "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "passed": len(passed),
        "failed": len(failed),
        "status": status_label,
        "tests": results
    }, f, indent=2)
print(f"  Report saved -> {report_path}\n")

sys.exit(0 if not failed else 1)
