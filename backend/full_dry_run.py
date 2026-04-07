"""
AI Policy Impact Simulator - Full End-to-End Dry Run
Tests every API endpoint, auth flow, ML pipeline, DB, and SPA fallback.
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

import requests
import json
import time

BASE = "http://localhost:8000"
PASS = "[PASS]"
FAIL = "[FAIL]"
results = []
token = None
test_email = f"dryrun_{int(time.time())}@test.com"
test_password = "TestPass123!"
test_name = "Dry Run User"


def test(name, func):
    """Run a test and record result."""
    global results
    try:
        ok, detail = func()
        status = PASS if ok else FAIL
        results.append((status, name, detail))
        print(f"  {status} {name}: {detail}")
        return ok
    except Exception as e:
        results.append((FAIL, name, str(e)))
        print(f"  {FAIL} {name}: {e}")
        return False


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ============================================================
#  1. SERVER & HEALTH
# ============================================================
section("1. SERVER & HEALTH CHECKS")

def test_health():
    r = requests.get(f"{BASE}/health", timeout=5)
    return r.status_code == 200 and r.json()["status"] == "healthy", f"Status={r.status_code}, Body={r.json()}"

def test_api_status():
    r = requests.get(f"{BASE}/api/status", timeout=5)
    return r.status_code == 200, f"Status={r.status_code}, Version={r.json().get('version')}"

def test_docs():
    r = requests.get(f"{BASE}/docs", timeout=5)
    return r.status_code == 200, f"Status={r.status_code}, Swagger UI accessible"

test("Health endpoint", test_health)
test("API status endpoint", test_api_status)
test("Swagger docs accessible", test_docs)


# ============================================================
#  2. SPA FALLBACK (404 FIX)
# ============================================================
section("2. SPA FALLBACK — ROUTES SERVE index.html (NOT 404)")

spa_routes = ["/", "/login", "/signup", "/simulator", "/dashboard", "/results", "/scenarios", "/some/random/path"]

for route in spa_routes:
    def make_test(r):
        def t():
            resp = requests.get(f"{BASE}{r}", timeout=5)
            has_html = 'id="root"' in resp.text or '<!DOCTYPE' in resp.text.upper() or resp.status_code == 200
            return resp.status_code == 200 and has_html, f"Status={resp.status_code}, HasHTML={has_html}, Size={len(resp.text)}b"
        return t
    test(f"SPA route: {route}", make_test(route))


# ============================================================
#  3. AUTHENTICATION
# ============================================================
section("3. AUTHENTICATION (Register → Login → Verify → Profile)")

def test_register():
    global token
    r = requests.post(f"{BASE}/auth/register", json={
        "email": test_email, "password": test_password, "name": test_name
    }, timeout=10)
    if r.status_code == 200:
        data = r.json()
        token = data.get("token")
        return bool(token) and "user" in data, f"Token={'yes' if token else 'NO'}, User={data.get('user', {}).get('email')}"
    return False, f"Status={r.status_code}, Body={r.text[:200]}"

def test_register_duplicate():
    r = requests.post(f"{BASE}/auth/register", json={
        "email": test_email, "password": test_password, "name": test_name
    }, timeout=10)
    return r.status_code == 400, f"Status={r.status_code} (expect 400 for duplicate)"

def test_login():
    global token
    r = requests.post(f"{BASE}/auth/login", json={
        "email": test_email, "password": test_password
    }, timeout=10)
    if r.status_code == 200:
        data = r.json()
        token = data.get("token")
        return bool(token), f"Token={'yes' if token else 'NO'}, Msg={data.get('message')}"
    return False, f"Status={r.status_code}"

def test_login_wrong_password():
    r = requests.post(f"{BASE}/auth/login", json={
        "email": test_email, "password": "wrongpassword"
    }, timeout=10)
    return r.status_code == 401, f"Status={r.status_code} (expect 401 for wrong password)"

def test_verify_token():
    r = requests.post(f"{BASE}/auth/verify", headers={"Authorization": f"Bearer {token}"}, timeout=5)
    return r.status_code == 200 and r.json().get("valid") == True, f"Status={r.status_code}, Valid={r.json().get('valid')}"

def test_no_token():
    r = requests.post(f"{BASE}/auth/verify", timeout=5)
    return r.status_code == 401 or r.status_code == 403, f"Status={r.status_code} (expect 401/403 without token)"

def test_me():
    r = requests.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=5)
    if r.status_code == 200:
        data = r.json()
        return data.get("email") == test_email, f"Email={data.get('email')}, Name={data.get('name')}"
    return False, f"Status={r.status_code}"

test("Register new user", test_register)
test("Reject duplicate registration", test_register_duplicate)
test("Login with correct credentials", test_login)
test("Reject wrong password", test_login_wrong_password)
test("Verify JWT token", test_verify_token)
test("Reject missing token", test_no_token)
test("Get user profile (/auth/me)", test_me)

headers = {"Authorization": f"Bearer {token}"}


# ============================================================
#  4. ML MODEL & PREDICTIONS
# ============================================================
section("4. ML MODEL — PREDICTION ENGINE")

def test_predict():
    r = requests.post(f"{BASE}/predict", json={
        "tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
        "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50
    }, headers=headers, timeout=15)
    if r.status_code == 200:
        d = r.json()
        keys = ['gdp_growth', 'inflation', 'employment_rate', 'environment_score', 'public_satisfaction', 'confidence']
        has_all = all(k in d for k in keys)
        return has_all, f"GDP={d.get('gdp_growth','?'):.2f}, Inflation={d.get('inflation','?'):.2f}, Confidence={d.get('confidence','?'):.2f}"
    return False, f"Status={r.status_code}, Body={r.text[:200]}"

def test_predict_extreme():
    r = requests.post(f"{BASE}/predict", json={
        "tax_rate": 55, "fuel_price": 9.0, "subsidy": 0,
        "public_spending": 55, "interest_rate": 18, "environmental_regulation": 5
    }, headers=headers, timeout=15)
    if r.status_code == 200:
        d = r.json()
        return 'gdp_growth' in d, f"GDP={d.get('gdp_growth','?'):.2f}, Employment={d.get('employment_rate','?'):.2f} (extreme scenario)"
    return False, f"Status={r.status_code}"

def test_predict_unauth():
    r = requests.post(f"{BASE}/predict", json={"tax_rate": 25}, timeout=5)
    return r.status_code in (401, 403), f"Status={r.status_code} (expect 401 without auth)"

def test_model_info():
    r = requests.get(f"{BASE}/model/info", timeout=5)
    if r.status_code == 200:
        d = r.json()
        return 'model_type' in d and 'r2_score' in d, f"Model={d.get('model_type')}, R²={d.get('r2_score','?'):.4f}, Samples={d.get('training_samples')}"
    return False, f"Status={r.status_code}"

def test_feature_importance():
    r = requests.get(f"{BASE}/model/feature-importance", timeout=5)
    if r.status_code == 200:
        d = r.json()
        return isinstance(d, list) and len(d) > 0, f"Features={len(d)}, Top={d[0].get('feature') if d else '?'}={d[0].get('importance','?')}"
    return False, f"Status={r.status_code}"

test("Predict with default inputs", test_predict)
test("Predict with extreme inputs", test_predict_extreme)
test("Reject prediction without auth", test_predict_unauth)
test("Get model info", test_model_info)
test("Get feature importance", test_feature_importance)


# ============================================================
#  5. SENSITIVITY ANALYSIS
# ============================================================
section("5. SENSITIVITY ANALYSIS")

def test_sensitivity():
    r = requests.post(f"{BASE}/sensitivity", json={
        "inputs": {"tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
                   "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50},
        "target_variable": "gdp_growth"
    }, headers=headers, timeout=15)
    if r.status_code == 200:
        d = r.json()
        if isinstance(d, list) and len(d) > 0:
            top = d[0]
            return True, f"Top impact: {top.get('feature')} → {top.get('impact','?'):.4f} ({top.get('direction')})"
    return False, f"Status={r.status_code}"

def test_sensitivity_inflation():
    r = requests.post(f"{BASE}/sensitivity", json={
        "target_variable": "inflation"
    }, headers=headers, timeout=15)
    return r.status_code == 200, f"Status={r.status_code}, Uses default inputs for inflation target"

test("Sensitivity analysis (GDP target)", test_sensitivity)
test("Sensitivity analysis (inflation target)", test_sensitivity_inflation)


# ============================================================
#  6. AI RECOMMENDATION
# ============================================================
section("6. AI POLICY RECOMMENDATION")

def test_recommend():
    r = requests.post(f"{BASE}/recommend", json={
        "gdp_growth": 4.0, "inflation": 2.5,
        "employment_rate": 96.0, "environment_score": 80.0
    }, headers=headers, timeout=30)
    if r.status_code == 200:
        d = r.json()
        ri = d.get("recommended_inputs", {})
        po = d.get("predicted_outcomes", {})
        return bool(ri) and bool(po), f"Tax={ri.get('tax_rate')}, Subsidy={ri.get('subsidy')}, PredGDP={po.get('gdp_growth','?')}"
    return False, f"Status={r.status_code}"

test("AI recommendation for target outcomes", test_recommend)


# ============================================================
#  7. SCENARIOS CRUD
# ============================================================
section("7. SCENARIOS — CREATE, LIST, COMPARE, DELETE")

scenario_id = None

def test_save_scenario():
    global scenario_id
    r = requests.post(f"{BASE}/scenarios", json={
        "name": "Dry Run Scenario A",
        "inputs": {"tax_rate": 20, "fuel_price": 3.0, "subsidy": 20,
                   "public_spending": 35, "interest_rate": 4, "environmental_regulation": 60},
        "results": {"gdp_growth": 3.5, "inflation": 2.8, "employment_rate": 95.2,
                    "environment_score": 72.1, "public_satisfaction": 68.5}
    }, headers=headers, timeout=10)
    if r.status_code == 200:
        d = r.json()
        scenario_id = d.get("id")
        return bool(scenario_id), f"Saved ID={scenario_id}, Name={d.get('name')}"
    return False, f"Status={r.status_code}"

def test_save_scenario_b():
    r = requests.post(f"{BASE}/scenarios", json={
        "name": "Dry Run Scenario B",
        "inputs": {"tax_rate": 35, "fuel_price": 5.0, "subsidy": 10,
                   "public_spending": 25, "interest_rate": 8, "environmental_regulation": 80},
        "results": {"gdp_growth": 1.2, "inflation": 4.1, "employment_rate": 91.5,
                    "environment_score": 85.3, "public_satisfaction": 55.2}
    }, headers=headers, timeout=10)
    return r.status_code == 200, f"Status={r.status_code}, Saved second scenario"

def test_list_scenarios():
    r = requests.get(f"{BASE}/scenarios", headers=headers, timeout=5)
    if r.status_code == 200:
        d = r.json()
        return isinstance(d, list) and len(d) >= 2, f"Count={len(d)}"
    return False, f"Status={r.status_code}"

def test_compare():
    r = requests.post(f"{BASE}/compare", json={
        "scenarios": [
            {"tax_rate": 20, "fuel_price": 3.0, "subsidy": 20,
             "public_spending": 35, "interest_rate": 4, "environmental_regulation": 60},
            {"tax_rate": 35, "fuel_price": 5.0, "subsidy": 10,
             "public_spending": 25, "interest_rate": 8, "environmental_regulation": 80}
        ]
    }, headers=headers, timeout=15)
    if r.status_code == 200:
        d = r.json()
        return isinstance(d, list) and len(d) == 2, f"Compared {len(d)} scenarios, GDP_A={d[0].get('gdp_growth','?'):.2f} vs GDP_B={d[1].get('gdp_growth','?'):.2f}"
    return False, f"Status={r.status_code}"

def test_delete_scenario():
    r = requests.delete(f"{BASE}/scenarios/{scenario_id}", headers=headers, timeout=5)
    return r.status_code == 200, f"Status={r.status_code}, Deleted ID={scenario_id}"

test("Save scenario A", test_save_scenario)
test("Save scenario B", test_save_scenario_b)
test("List all scenarios", test_list_scenarios)
test("Compare 2 scenarios", test_compare)
test("Delete scenario A", test_delete_scenario)


# ============================================================
#  8. SIMULATION HISTORY
# ============================================================
section("8. SIMULATION HISTORY")

def test_history():
    r = requests.get(f"{BASE}/history", headers=headers, timeout=5)
    if r.status_code == 200:
        d = r.json()
        if isinstance(d, list) and len(d) > 0:
            latest = d[0]
            return True, f"Count={len(d)}, Latest model={latest.get('model_type')}, Confidence={latest.get('confidence','?')}"
        return True, f"Count=0 (empty but endpoint works)"
    return False, f"Status={r.status_code}"

test("Get simulation history", test_history)


# ============================================================
#  9. STATIC ASSETS
# ============================================================
section("9. STATIC ASSETS & PRODUCTION BUILD")

def test_index_html():
    r = requests.get(f"{BASE}/", timeout=5)
    return r.status_code == 200 and 'id="root"' in r.text, f"Status={r.status_code}, HasReactRoot={'id=\"root\"' in r.text}"

def test_assets_css():
    r = requests.get(f"{BASE}/", timeout=5)
    # Extract CSS filename from index.html
    import re
    match = re.search(r'href="/assets/(index-[^"]+\.css)"', r.text)
    if match:
        css_url = f"{BASE}/assets/{match.group(1)}"
        r2 = requests.get(css_url, timeout=5)
        return r2.status_code == 200, f"CSS file: {match.group(1)}, Size={len(r2.text)}b"
    return False, "Could not find CSS link in index.html"

def test_assets_js():
    r = requests.get(f"{BASE}/", timeout=5)
    import re
    match = re.search(r'src="/assets/(index-[^"]+\.js)"', r.text)
    if match:
        js_url = f"{BASE}/assets/{match.group(1)}"
        r2 = requests.get(js_url, timeout=5)
        return r2.status_code == 200, f"JS bundle: {match.group(1)}, Size={len(r2.text)//1024}KB"
    return False, "Could not find JS bundle in index.html"

test("index.html serves React app", test_index_html)
test("CSS assets load correctly", test_assets_css)
test("JS bundle loads correctly", test_assets_js)


# ============================================================
#  FINAL SUMMARY
# ============================================================
section("DRY RUN SUMMARY")

passed = sum(1 for s, _, _ in results if s == PASS)
failed = sum(1 for s, _, _ in results if s == FAIL)
total = len(results)

print(f"\n  Total Tests: {total}")
print(f"  Passed:      {passed} {PASS}")
print(f"  Failed:      {failed} {FAIL if failed else ''}")
print(f"  Pass Rate:   {passed/total*100:.1f}%")
print()

if failed > 0:
    print("  Failed tests:")
    for s, name, detail in results:
        if s == FAIL:
            print(f"    • {name}: {detail}")
    print()

if failed == 0:
    print("  ALL TESTS PASSED -- APPLICATION IS FULLY FUNCTIONAL!")
else:
    print(f"  WARNING: {failed} test(s) need attention.")

print(f"\n{'='*60}\n")
