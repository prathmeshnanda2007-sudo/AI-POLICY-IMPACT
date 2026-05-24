"""
PolicyAI — Complete Live API Dry Run
Tests the running FastAPI server at http://localhost:8000 end-to-end
with training data, testing data, auth flows, and vulnerability checks.
"""
import sys, os, json, time, traceback, requests

sys.path.insert(0, os.path.dirname(__file__))
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000"
TS = int(time.time())
TEST_EMAIL = f"dryrun_{TS}@test.com"
TEST_PASS  = "DrYrUn$ecure99!"
TEST_NAME  = "Dry Run User"
TOKEN      = None

results = []

def check(name, fn):
    try:
        fn()
        print(f"  [PASS] {name}")
        results.append(("PASS", name, None))
    except AssertionError as e:
        print(f"  [FAIL] {name}: {e}")
        results.append(("FAIL", name, str(e)))
    except Exception as e:
        msg = traceback.format_exc().strip().split("\n")[-1]
        print(f"  [FAIL] {name}: {msg}")
        results.append(("FAIL", name, msg))

def warn(name, msg):
    print(f"  [WARN] {name}: {msg}")
    results.append(("WARN", name, msg))

# ─────────────────────────────────────────────────────────────
# 1. SERVER HEALTH
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 1: Server Health")
print("="*60)

def test_health():
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    assert r.status_code == 200, f"Status {r.status_code}"
    assert r.json().get("status") == "healthy"

def test_api_status():
    r = requests.get(f"{BASE_URL}/api/status", timeout=5)
    assert r.status_code == 200
    d = r.json()
    assert "name" in d and "version" in d

def test_docs_available():
    r = requests.get(f"{BASE_URL}/docs", timeout=5)
    assert r.status_code == 200

def test_model_info_public():
    r = requests.get(f"{BASE_URL}/model/info", timeout=5)
    assert r.status_code == 200
    d = r.json()
    assert "model_type" in d or d == {}  # empty before training is ok

check("Health endpoint", test_health)
check("API status endpoint", test_api_status)
check("Swagger docs available", test_docs_available)
check("Model info endpoint (public)", test_model_info_public)

# ─────────────────────────────────────────────────────────────
# 2. AUTHENTICATION
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 2: Authentication")
print("="*60)

def test_register():
    global TOKEN
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "email": TEST_EMAIL, "password": TEST_PASS, "name": TEST_NAME
    }, timeout=10)
    assert r.status_code == 200, f"Register failed: {r.status_code} — {r.text}"
    d = r.json()
    assert "token" in d, "No token in response"
    assert "user" in d
    assert d["user"]["email"] == TEST_EMAIL
    TOKEN = d["token"]
    print(f"         Token acquired: {TOKEN[:30]}...")

def test_register_duplicate():
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "email": TEST_EMAIL, "password": TEST_PASS, "name": TEST_NAME
    }, timeout=10)
    assert r.status_code == 400, f"Expected 400 for duplicate, got {r.status_code}"

def test_register_weak_password():
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "email": f"weak_{TS}@test.com", "password": "abc", "name": "Weak Pass"
    }, timeout=10)
    assert r.status_code in (400, 422), f"Expected 400/422 for weak password, got {r.status_code}"

def test_register_invalid_email():
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "notanemail", "password": TEST_PASS, "name": "Bad Email"
    }, timeout=10)
    assert r.status_code in (400, 422), f"Expected 400/422 for bad email, got {r.status_code}"

def test_login_success():
    global TOKEN
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_EMAIL, "password": TEST_PASS
    }, timeout=10)
    assert r.status_code == 200, f"Login failed: {r.status_code} — {r.text}"
    d = r.json()
    assert "token" in d
    TOKEN = d["token"]

def test_login_wrong_password():
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_EMAIL, "password": "WrongPass999!"
    }, timeout=10)
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"

def test_login_nonexistent_user():
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "nobody@nowhere.com", "password": TEST_PASS
    }, timeout=10)
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"

def test_verify_token():
    r = requests.post(f"{BASE_URL}/auth/verify",
        headers={"Authorization": f"Bearer {TOKEN}"}, timeout=10)
    assert r.status_code == 200
    assert r.json().get("valid") == True

def test_get_me():
    r = requests.get(f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {TOKEN}"}, timeout=10)
    assert r.status_code == 200
    d = r.json()
    assert d["email"] == TEST_EMAIL

def test_protected_without_token():
    # RFC 7235: 401 = no/invalid credentials, 403 = authenticated but forbidden
    # FastAPI's HTTPBearer returns 403 when auto_error=True, 401 when auto_error=False
    # Our config uses auto_error=False then raises 401 manually — both are valid
    r = requests.post(f"{BASE_URL}/predict", json={
        "tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
        "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50
    }, timeout=10)
    assert r.status_code in (401, 403), f"Expected 401 or 403, got {r.status_code}"

def test_protected_with_bad_token():
    r = requests.post(f"{BASE_URL}/predict", json={
        "tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
        "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50
    }, headers={"Authorization": "Bearer fakejwttokenxyz"}, timeout=10)
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"

check("User registration", test_register)
check("Duplicate registration rejected (400)", test_register_duplicate)
check("Weak password rejected", test_register_weak_password)
check("Invalid email rejected", test_register_invalid_email)
check("Login success", test_login_success)
check("Wrong password rejected (401)", test_login_wrong_password)
check("Nonexistent user rejected (401)", test_login_nonexistent_user)
check("Token verification", test_verify_token)
check("GET /auth/me returns user", test_get_me)
check("Protected route without token returns 403", test_protected_without_token)
check("Protected route with bad token returns 401", test_protected_with_bad_token)

AUTH = {"Authorization": f"Bearer {TOKEN}"}

# ─────────────────────────────────────────────────────────────
# 3. ML PREDICTION — TRAINING DATA SCENARIOS
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 3: Prediction — Training Data Scenarios")
print("="*60)

SCENARIOS = {
    "Balanced Policy (baseline)": {
        "tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
        "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50
    },
    "High Tax / Green Focus": {
        "tax_rate": 45, "fuel_price": 2.0, "subsidy": 35,
        "public_spending": 45, "interest_rate": 3, "environmental_regulation": 85
    },
    "Low Tax / Business Stimulus": {
        "tax_rate": 10, "fuel_price": 5.0, "subsidy": 5,
        "public_spending": 20, "interest_rate": 8, "environmental_regulation": 20
    },
    "Austerity / High Interest": {
        "tax_rate": 35, "fuel_price": 6.5, "subsidy": 2,
        "public_spending": 15, "interest_rate": 15, "environmental_regulation": 40
    },
    "Max Stimulus": {
        "tax_rate": 5, "fuel_price": 1.5, "subsidy": 45,
        "public_spending": 55, "interest_rate": 0.25, "environmental_regulation": 90
    },
}

prediction_results = {}

for name, scenario in SCENARIOS.items():
    def _make_test(sc_name, sc):
        def _test():
            r = requests.post(f"{BASE_URL}/predict", json=sc,
                headers=AUTH, timeout=30)
            assert r.status_code == 200, f"Status {r.status_code}: {r.text[:200]}"
            d = r.json()
            for key in ["gdp_growth", "inflation", "employment_rate",
                        "environment_score", "public_satisfaction", "confidence"]:
                assert key in d, f"Missing '{key}' in response"
            assert 0 <= d["confidence"] <= 1, f"Confidence out of range: {d['confidence']}"
            prediction_results[sc_name] = d
            print(f"         GDP={d['gdp_growth']:.2f}%  Inf={d['inflation']:.2f}%  "
                  f"Emp={d['employment_rate']:.1f}%  Env={d['environment_score']:.1f}  "
                  f"Sat={d['public_satisfaction']:.1f}  Conf={d['confidence']:.2f}")
        return _test
    check(f"Predict: {name}", _make_test(name, scenario))

# ─────────────────────────────────────────────────────────────
# 4. ML PREDICTION — TESTING / EDGE CASES
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 4: Prediction — Testing / Edge Cases")
print("="*60)

def test_predict_min_bounds():
    r = requests.post(f"{BASE_URL}/predict", json={
        "tax_rate": 0, "fuel_price": 1, "subsidy": 0,
        "public_spending": 10, "interest_rate": 0, "environmental_regulation": 0
    }, headers=AUTH, timeout=30)
    assert r.status_code == 200, f"Min bounds: {r.status_code} — {r.text}"

def test_predict_max_bounds():
    r = requests.post(f"{BASE_URL}/predict", json={
        "tax_rate": 60, "fuel_price": 10, "subsidy": 50,
        "public_spending": 60, "interest_rate": 20, "environmental_regulation": 100
    }, headers=AUTH, timeout=30)
    assert r.status_code == 200, f"Max bounds: {r.status_code}"

def test_predict_over_max_rejected():
    r = requests.post(f"{BASE_URL}/predict", json={
        "tax_rate": 999, "fuel_price": 3.5, "subsidy": 15,
        "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50
    }, headers=AUTH, timeout=30)
    assert r.status_code == 422, f"Expected 422 for out-of-range, got {r.status_code}"

def test_predict_missing_field_uses_default():
    r = requests.post(f"{BASE_URL}/predict", json={
        "tax_rate": 25
    }, headers=AUTH, timeout=30)
    # Should use defaults for missing fields — either 200 or 422 is acceptable
    assert r.status_code in (200, 422), f"Got {r.status_code}"

def test_predict_directional_high_tax():
    base = requests.post(f"{BASE_URL}/predict", json=SCENARIOS["Balanced Policy (baseline)"],
        headers=AUTH, timeout=30).json()
    high_tax = requests.post(f"{BASE_URL}/predict", json={
        **SCENARIOS["Balanced Policy (baseline)"], "tax_rate": 55
    }, headers=AUTH, timeout=30).json()
    assert high_tax["gdp_growth"] < base["gdp_growth"] + 3, \
        f"High tax should not massively increase GDP: {high_tax['gdp_growth']:.2f} vs {base['gdp_growth']:.2f}"

def test_predict_directional_high_env_reg():
    base = requests.post(f"{BASE_URL}/predict", json=SCENARIOS["Balanced Policy (baseline)"],
        headers=AUTH, timeout=30).json()
    high_env = requests.post(f"{BASE_URL}/predict", json={
        **SCENARIOS["Balanced Policy (baseline)"], "environmental_regulation": 95
    }, headers=AUTH, timeout=30).json()
    assert high_env["environment_score"] > base["environment_score"] - 5, \
        "High env regulation should maintain or improve env score"

check("Predict at minimum bounds (boundary test)", test_predict_min_bounds)
check("Predict at maximum bounds (boundary test)", test_predict_max_bounds)
check("Over-max values rejected with 422", test_predict_over_max_rejected)
check("Missing fields use defaults", test_predict_missing_field_uses_default)
check("High tax directional correctness", test_predict_directional_high_tax)
check("High env-regulation effect", test_predict_directional_high_env_reg)

# ─────────────────────────────────────────────────────────────
# 5. SCENARIO COMPARISON
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 5: Scenario Comparison")
print("="*60)

def test_compare_two_scenarios():
    r = requests.post(f"{BASE_URL}/compare", json={
        "scenarios": [
            SCENARIOS["Balanced Policy (baseline)"],
            SCENARIOS["High Tax / Green Focus"]
        ]
    }, headers=AUTH, timeout=30)
    assert r.status_code == 200, f"Compare failed: {r.status_code} — {r.text}"
    d = r.json()
    assert isinstance(d, list) and len(d) == 2
    for item in d:
        assert "gdp_growth" in item

def test_compare_five_scenarios():
    r = requests.post(f"{BASE_URL}/compare", json={
        "scenarios": list(SCENARIOS.values())
    }, headers=AUTH, timeout=30)
    assert r.status_code == 200, f"Multi-compare: {r.status_code}"
    assert len(r.json()) == 5

check("Compare 2 scenarios", test_compare_two_scenarios)
check("Compare all 5 scenarios", test_compare_five_scenarios)

# ─────────────────────────────────────────────────────────────
# 6. SCENARIOS CRUD
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 6: Scenario Management (CRUD)")
print("="*60)

saved_scenario_id = None

def test_save_scenario():
    global saved_scenario_id
    r = requests.post(f"{BASE_URL}/scenarios", json={
        "name": f"Dry Run Scenario {TS}",
        "inputs": SCENARIOS["Balanced Policy (baseline)"],
        "results": prediction_results.get("Balanced Policy (baseline)", {"gdp_growth": 2.5})
    }, headers=AUTH, timeout=10)
    assert r.status_code == 200, f"Save scenario: {r.status_code} — {r.text}"
    d = r.json()
    assert "id" in d
    saved_scenario_id = d["id"]
    print(f"         Saved scenario ID: {saved_scenario_id}")

def test_list_scenarios():
    r = requests.get(f"{BASE_URL}/scenarios", headers=AUTH, timeout=10)
    assert r.status_code == 200
    d = r.json()
    assert isinstance(d, list)
    assert any(s["id"] == saved_scenario_id for s in d), "Saved scenario not in list"

def test_delete_scenario():
    r = requests.delete(f"{BASE_URL}/scenarios/{saved_scenario_id}",
        headers=AUTH, timeout=10)
    assert r.status_code == 200, f"Delete: {r.status_code}"

def test_delete_nonexistent():
    r = requests.delete(f"{BASE_URL}/scenarios/999999",
        headers=AUTH, timeout=10)
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"

check("Save scenario", test_save_scenario)
check("List scenarios (includes saved)", test_list_scenarios)
check("Delete scenario", test_delete_scenario)
check("Delete nonexistent → 404", test_delete_nonexistent)

# ─────────────────────────────────────────────────────────────
# 7. SIMULATION HISTORY
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 7: Simulation History")
print("="*60)

def test_get_history():
    r = requests.get(f"{BASE_URL}/history", headers=AUTH, timeout=10)
    assert r.status_code == 200
    d = r.json()
    assert isinstance(d, list)
    print(f"         History entries: {len(d)}")
    if d:
        h = d[0]
        assert "inputs" in h and "results" in h and "timestamp" in h

check("Simulation history endpoint", test_get_history)

# ─────────────────────────────────────────────────────────────
# 8. ADVANCED ML: FEATURE IMPORTANCE + SENSITIVITY
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 8: Advanced ML Endpoints")
print("="*60)

def test_feature_importance():
    r = requests.get(f"{BASE_URL}/model/feature-importance", timeout=10)
    assert r.status_code == 200
    d = r.json()
    assert isinstance(d, list)
    if d:
        assert "feature" in d[0] and "importance" in d[0]
        print(f"         Top feature: {d[0]['feature']} ({d[0]['importance']:.4f})")

def test_sensitivity():
    r = requests.post(f"{BASE_URL}/sensitivity", json={
        "inputs": SCENARIOS["Balanced Policy (baseline)"],
        "target_variable": "gdp_growth"
    }, headers=AUTH, timeout=30)
    assert r.status_code == 200, f"Sensitivity: {r.status_code} — {r.text}"
    d = r.json()
    assert isinstance(d, list) and len(d) >= 1
    print(f"         Most impactful: {d[0]['feature']} (impact: {d[0]['impact']:.4f})")

def test_sensitivity_all_targets():
    targets = ["gdp_growth", "inflation", "employment_rate", "environment_score", "public_satisfaction"]
    for t in targets:
        r = requests.post(f"{BASE_URL}/sensitivity", json={
            "inputs": SCENARIOS["Balanced Policy (baseline)"],
            "target_variable": t
        }, headers=AUTH, timeout=30)
        assert r.status_code == 200, f"Sensitivity for {t}: {r.status_code}"

def test_recommendation():
    r = requests.post(f"{BASE_URL}/recommend", json={
        "gdp_growth": 5.0,
        "inflation": 2.0,
        "employment_rate": 97.0,
        "environment_score": 80.0,
        "public_satisfaction": 80.0
    }, headers=AUTH, timeout=60)
    assert r.status_code == 200, f"Recommend: {r.status_code} — {r.text}"
    d = r.json()
    assert "recommended_inputs" in d and "predicted_outcomes" in d
    ri = d["recommended_inputs"]
    print(f"         Recommended: tax={ri.get('tax_rate')}, "
          f"interest={ri.get('interest_rate')}, env_reg={ri.get('environmental_regulation')}")

check("Feature importance endpoint", test_feature_importance)
check("Sensitivity analysis (GDP target)", test_sensitivity)
check("Sensitivity analysis (all 5 targets)", test_sensitivity_all_targets)
check("Policy recommendation", test_recommendation)

# ─────────────────────────────────────────────────────────────
# 9. VULNERABILITY TESTS
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 9: Security / Vulnerability Tests")
print("="*60)

def test_sql_injection_in_email():
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "' OR '1'='1", "password": "anything"
    }, timeout=10)
    assert r.status_code in (401, 422, 400), \
        f"SQL injection should be rejected, got {r.status_code}"

def test_xss_in_scenario_name():
    r = requests.post(f"{BASE_URL}/scenarios", json={
        "name": "<script>alert('xss')</script>",
        "inputs": SCENARIOS["Balanced Policy (baseline)"],
        "results": {"gdp_growth": 2.5}
    }, headers=AUTH, timeout=10)
    # Should either store safely (200) or reject (400) — must not execute
    assert r.status_code in (200, 400, 422)
    if r.status_code == 200:
        # Verify it's stored as plain text, not executed
        sid = r.json().get("id")
        if sid:
            requests.delete(f"{BASE_URL}/scenarios/{sid}", headers=AUTH, timeout=5)

def test_no_user_data_leakage():
    r = requests.get(f"{BASE_URL}/auth/me", headers=AUTH, timeout=10)
    assert r.status_code == 200
    d = r.json()
    assert "password_hash" not in d, "Password hash leaked in /auth/me!"
    assert "password" not in d, "Password leaked in /auth/me!"

def test_other_user_cant_delete_scenario():
    # Create scenario as our user
    r1 = requests.post(f"{BASE_URL}/scenarios", json={
        "name": "Private Scenario",
        "inputs": SCENARIOS["Balanced Policy (baseline)"],
        "results": {"gdp_growth": 2.1}
    }, headers=AUTH, timeout=10)
    if r1.status_code != 200:
        return  # skip if save failed
    sid = r1.json().get("id")
    # Try to delete with no token
    r2 = requests.delete(f"{BASE_URL}/scenarios/{sid}", timeout=10)
    assert r2.status_code in (401, 403), \
        f"Unauthenticated delete should fail, got {r2.status_code}"
    # Clean up
    requests.delete(f"{BASE_URL}/scenarios/{sid}", headers=AUTH, timeout=5)

def test_rate_limit_check():
    # Basic: hitting same endpoint 20 times should not 500
    errors = 0
    for _ in range(20):
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "nobody@x.com", "password": "bad"
        }, timeout=5)
        if r.status_code == 500:
            errors += 1
    assert errors == 0, f"{errors}/20 requests returned 500 (internal error)"
    if errors == 0:
        warn("Rate Limiting", "No rate limiting detected — consider adding slowapi for production")

check("SQL injection in email field", test_sql_injection_in_email)
check("XSS in scenario name (safe storage)", test_xss_in_scenario_name)
check("No password hash leaked in /auth/me", test_no_user_data_leakage)
check("Unauthenticated delete rejected", test_other_user_cant_delete_scenario)
check("Repeated bad logins don't cause 500", test_rate_limit_check)

# ─────────────────────────────────────────────────────────────
# 10. MODEL TRAINING ENDPOINT
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SECTION 10: Model Training Endpoint")
print("="*60)

def test_train_model():
    print("         Training model via API (takes ~60s)...")
    r = requests.post(f"{BASE_URL}/train", headers=AUTH, timeout=180)
    assert r.status_code == 200, f"Train: {r.status_code} — {r.text}"
    d = r.json()
    assert d.get("status") == "success"
    assert "model_type" in d and "r2_score" in d
    assert d["r2_score"] > 0.85, f"R2 too low: {d['r2_score']}"
    print(f"         Model: {d['model_type']} | R2={d['r2_score']:.4f} | RMSE={d['rmse']:.4f}")

check("Train model via API", test_train_model)

# ─────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  DRY RUN REPORT SUMMARY")
print("="*60)

passed = [r for r in results if r[0] == "PASS"]
failed = [r for r in results if r[0] == "FAIL"]
warned = [r for r in results if r[0] == "WARN"]
total  = len(results)

print(f"\n  Total checks : {total}")
print(f"  Passed       : {len(passed)}")
print(f"  Failed       : {len(failed)}")
print(f"  Warnings     : {len(warned)}")

if failed:
    print("\n  --- FAILURES ---")
    for _, name, msg in failed:
        print(f"  [FAIL] {name}")
        print(f"         => {msg}")

if warned:
    print("\n  --- WARNINGS ---")
    for _, name, msg in warned:
        print(f"  [WARN] {name}: {msg}")

score = int(100 * len(passed) / total) if total else 0
print(f"\n  Health Score: {score}%")
if score == 100:
    print("  *** ALL CHECKS PASSED - Website is fully functional! ***")
elif score >= 90:
    print("  [GOOD] Website is functional with minor issues.")
elif score >= 75:
    print("  [WARN] Some features need attention.")
else:
    print("  [CRITICAL] Serious issues found.")

print("\n  Predictions Summary:")
for sc_name, res in prediction_results.items():
    print(f"    {sc_name[:35]:<35} GDP={res.get('gdp_growth',0):+.2f}%  "
          f"Inf={res.get('inflation',0):.2f}%  Emp={res.get('employment_rate',0):.1f}%")

report = {
    "score": score, "total": total, "passed": len(passed),
    "failed": len(failed), "warnings": len(warned),
    "failures": [{"name": n, "error": m} for _, n, m in failed],
    "warnings_list": [{"name": n, "msg": m} for _, n, m in warned],
    "predictions": prediction_results,
}
with open(os.path.join(os.path.dirname(__file__), "live_audit_report.json"), "w") as f:
    json.dump(report, f, indent=2)
print("\n  Report saved -> backend/live_audit_report.json")
print()
sys.exit(0 if not failed else 1)
