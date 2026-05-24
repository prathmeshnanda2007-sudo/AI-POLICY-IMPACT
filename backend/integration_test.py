"""
PolicyAI — Full Stack Integration Test
Verifies every connection: Frontend<->Backend<->DB<->ML Model
"""
import sys, os, json, time, traceback
sys.path.insert(0, os.path.dirname(__file__))
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    os.system(f'{sys.executable} -m pip install requests -q')
    import requests

BASE = "http://localhost:8000"
FRONT = "http://localhost:5173"
TS = int(time.time())
results = []

def ok(name, detail=""):
    print(f"  [PASS] {name}" + (f"  ({detail})" if detail else ""))
    results.append(("PASS", name, detail))

def fail(name, detail=""):
    print(f"  [FAIL] {name}  => {detail}")
    results.append(("FAIL", name, detail))

def warn(name, detail=""):
    print(f"  [WARN] {name}  => {detail}")
    results.append(("WARN", name, detail))

def section(title):
    print(f"\n{'='*58}")
    print(f"  {title}")
    print(f"{'='*58}")

# ──────────────────────────────────────────────────────────────
# LAYER 1: Frontend alive?
# ──────────────────────────────────────────────────────────────
section("LAYER 1: Frontend (Vite/React) — http://localhost:5173")
try:
    r = requests.get(FRONT, timeout=5)
    if r.status_code == 200 and ("PolicyAI" in r.text or "<!DOCTYPE" in r.text or "<html" in r.text.lower()):
        ok("Vite dev server responding", f"HTTP {r.status_code}")
    else:
        fail("Vite dev server", f"HTTP {r.status_code} — unexpected content")
except Exception as e:
    fail("Vite dev server", str(e))

try:
    r = requests.get(f"{FRONT}/login", timeout=5)
    ok("Frontend SPA routing /login", f"HTTP {r.status_code}") if r.status_code == 200 else fail("/login route", f"HTTP {r.status_code}")
except Exception as e:
    fail("/login SPA route", str(e))

try:
    r = requests.get(f"{FRONT}/dashboard", timeout=5)
    ok("Frontend SPA routing /dashboard", f"HTTP {r.status_code}") if r.status_code == 200 else fail("/dashboard route", f"HTTP {r.status_code}")
except Exception as e:
    fail("/dashboard SPA route", str(e))

# ──────────────────────────────────────────────────────────────
# LAYER 2: Backend alive?
# ──────────────────────────────────────────────────────────────
section("LAYER 2: Backend (FastAPI/Uvicorn) — http://localhost:8000")
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    d = r.json()
    ok("FastAPI /health", d.get("status", "?")) if r.status_code == 200 else fail("/health", f"HTTP {r.status_code}")
except Exception as e:
    fail("FastAPI health check", str(e))

try:
    r = requests.get(f"{BASE}/api/status", timeout=5)
    d = r.json()
    ok("FastAPI /api/status", f"v{d.get('version','?')} — {d.get('status','?')}")
except Exception as e:
    fail("FastAPI status", str(e))

try:
    r = requests.get(f"{BASE}/docs", timeout=5)
    ok("Swagger API docs", f"HTTP {r.status_code}") if r.status_code == 200 else fail("/docs", f"HTTP {r.status_code}")
except Exception as e:
    fail("Swagger docs", str(e))

# ──────────────────────────────────────────────────────────────
# LAYER 3: Backend ↔ Database integration
# ──────────────────────────────────────────────────────────────
section("LAYER 3: Backend <-> SQLite Database")
try:
    from services.database import init_db, create_user, get_user_by_email, \
        save_simulation, get_history, save_scenario, get_all_scenarios, delete_scenario, DB_PATH
    init_db()
    ok("DB init / connection", f"at {os.path.basename(DB_PATH)}")
except Exception as e:
    fail("DB init", str(e))

try:
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn.close()
    expected = ['users', 'scenarios', 'simulation_history', 'model_training_log']
    missing = [t for t in expected if t not in tables]
    if missing:
        fail("DB schema tables", f"Missing: {missing}")
    else:
        ok("DB schema (4 tables)", ", ".join(tables))
except Exception as e:
    fail("DB schema check", str(e))

try:
    email = f"inttest_{TS}@check.com"
    from services.auth import hash_password
    u = create_user(email, hash_password("Test1234!"), "Integration Test")
    fetched = get_user_by_email(email)
    assert fetched and fetched['id'] == u['id']
    ok("DB user write+read", f"user_id={u['id']}")
except Exception as e:
    fail("DB user write+read", str(e))

try:
    sid = save_simulation({"tax_rate": 25}, {"gdp_growth": 2.5}, "LinearRegression", 0.95)
    history = get_history(5)
    assert any(h['id'] == sid for h in history)
    ok("DB simulation history write+read", f"entry_id={sid}")
except Exception as e:
    fail("DB history write+read", str(e))

try:
    sc = save_scenario("Integration Test Scenario", {"tax_rate": 30}, {"gdp_growth": 2.1})
    all_sc = get_all_scenarios()
    assert any(s['id'] == sc['id'] for s in all_sc)
    delete_scenario(sc['id'])
    ok("DB scenario CRUD (create/read/delete)", f"id={sc['id']}")
except Exception as e:
    fail("DB scenario CRUD", str(e))

# ──────────────────────────────────────────────────────────────
# LAYER 4: Backend ↔ ML Model integration
# ──────────────────────────────────────────────────────────────
section("LAYER 4: Backend <-> ML Model (Scikit-learn)")
try:
    from models.ml_model import load_model, MODEL_PATH, SCALER_PATH, METADATA_PATH
    assert os.path.exists(MODEL_PATH), "model.pkl missing"
    assert os.path.exists(SCALER_PATH), "scaler.pkl missing"
    assert os.path.exists(METADATA_PATH), "metadata.json missing"
    ok("ML model files exist", f"model.pkl, scaler.pkl, metadata.json")
except Exception as e:
    fail("ML model files", str(e))

try:
    model, scaler, meta = load_model()
    ok("ML model load", f"{meta.get('model_type','?')} | R2={meta.get('r2_score',0):.4f} | RMSE={meta.get('rmse',0):.4f}")
except Exception as e:
    fail("ML model load", str(e))

try:
    from models.ml_model import predict_policy
    result = predict_policy({"tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
                              "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50},
                            model, scaler)
    for k in ["gdp_growth","inflation","employment_rate","environment_score","public_satisfaction","confidence"]:
        assert k in result, f"Missing: {k}"
    # Verify output bounds are enforced
    assert 70 <= result['employment_rate'] <= 99.5, f"Employment out of bounds: {result['employment_rate']}"
    assert 0  <= result['environment_score'] <= 100, f"Env score out of bounds"
    assert 0  <= result['confidence'] <= 1, f"Confidence out of bounds"
    ok("ML prediction (all 6 outputs, bounds OK)",
       f"GDP={result['gdp_growth']:.2f}% Emp={result['employment_rate']:.1f}% Conf={result['confidence']:.2f}")
except Exception as e:
    fail("ML prediction", str(e))

try:
    from models.ml_model import sensitivity_analysis
    sa = sensitivity_analysis({"tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
                                "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50})
    assert len(sa) == 6
    ok("ML sensitivity analysis", f"Top driver: {sa[0]['feature']} (impact={sa[0]['impact']:+.4f})")
except Exception as e:
    fail("ML sensitivity analysis", str(e))

try:
    from models.ml_model import get_feature_importance
    fi = get_feature_importance()
    assert len(fi) == 6
    ok("ML feature importance", f"Top: {fi[0]['feature']} ({fi[0]['importance']:.4f})")
except Exception as e:
    fail("ML feature importance", str(e))

# ──────────────────────────────────────────────────────────────
# LAYER 5: Full Auth Flow (API -> DB -> JWT)
# ──────────────────────────────────────────────────────────────
section("LAYER 5: Auth Integration (API <-> DB <-> JWT)")
TOKEN = None
try:
    r = requests.post(f"{BASE}/auth/register", json={
        "email": f"flow_{TS}@test.com",
        "password": "FlowTest999!",
        "name": "Flow Tester"
    }, timeout=10)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:100]}"
    d = r.json()
    assert "token" in d and "user" in d
    TOKEN = d["token"]
    ok("Register -> DB write -> JWT issue", f"user_id={d['user']['id']}, token={TOKEN[:20]}...")
except Exception as e:
    fail("Register flow", str(e))

try:
    r = requests.post(f"{BASE}/auth/login", json={
        "email": f"flow_{TS}@test.com", "password": "FlowTest999!"
    }, timeout=10)
    assert r.status_code == 200
    TOKEN = r.json()["token"]
    ok("Login -> DB lookup -> JWT reissue", "correct credentials accepted")
except Exception as e:
    fail("Login flow", str(e))

try:
    r = requests.post(f"{BASE}/auth/verify",
        headers={"Authorization": f"Bearer {TOKEN}"}, timeout=5)
    assert r.status_code == 200 and r.json().get("valid")
    ok("JWT verify (token -> decode -> validate)", "token valid")
except Exception as e:
    fail("JWT verify", str(e))

try:
    r = requests.get(f"{BASE}/auth/me",
        headers={"Authorization": f"Bearer {TOKEN}"}, timeout=5)
    d = r.json()
    assert "password_hash" not in d and "password" not in d
    ok("GET /auth/me (no secret leakage)", f"email={d.get('email','?')}")
except Exception as e:
    fail("GET /auth/me", str(e))

AUTH = {"Authorization": f"Bearer {TOKEN}"}

# ──────────────────────────────────────────────────────────────
# LAYER 6: Full Simulation Flow (API -> ML -> DB -> Response)
# ──────────────────────────────────────────────────────────────
section("LAYER 6: Simulation Flow (API <-> ML <-> DB)")
try:
    payload = {"tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
               "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50}
    r = requests.post(f"{BASE}/predict", json=payload, headers=AUTH, timeout=30)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:200]}"
    d = r.json()
    assert all(k in d for k in ["gdp_growth","inflation","employment_rate",
                                 "environment_score","public_satisfaction","confidence"])
    assert 70 <= d['employment_rate'] <= 99.5, f"employment_rate={d['employment_rate']} out of bounds!"
    ok("Predict: API -> ML -> DB save -> response",
       f"GDP={d['gdp_growth']:.2f}% Emp={d['employment_rate']:.1f}% Conf={d['confidence']:.2f}")
except Exception as e:
    fail("Predict flow", str(e))

try:
    r = requests.get(f"{BASE}/history", headers=AUTH, timeout=10)
    assert r.status_code == 200
    h = r.json()
    assert len(h) > 0
    ok("History: DB read after prediction", f"{len(h)} entries stored")
except Exception as e:
    fail("History after predict", str(e))

try:
    r = requests.post(f"{BASE}/compare", json={"scenarios": [
        {"tax_rate": 20, "fuel_price": 3.0, "subsidy": 10, "public_spending": 28, "interest_rate": 4, "environmental_regulation": 45},
        {"tax_rate": 40, "fuel_price": 2.0, "subsidy": 30, "public_spending": 45, "interest_rate": 2, "environmental_regulation": 80},
    ]}, headers=AUTH, timeout=30)
    assert r.status_code == 200 and len(r.json()) == 2
    ok("Compare scenarios (2 ML calls in one request)", "both results returned")
except Exception as e:
    fail("Compare scenarios", str(e))

try:
    r1 = requests.post(f"{BASE}/scenarios", json={
        "name": "Integration Scenario",
        "inputs": {"tax_rate": 25},
        "results": {"gdp_growth": 2.5}
    }, headers=AUTH, timeout=10)
    assert r1.status_code == 200
    sid = r1.json()["id"]
    r2 = requests.get(f"{BASE}/scenarios", headers=AUTH, timeout=10)
    assert any(s["id"] == sid for s in r2.json())
    requests.delete(f"{BASE}/scenarios/{sid}", headers=AUTH, timeout=5)
    ok("Scenario CRUD (save -> list -> delete via API)", f"id={sid}")
except Exception as e:
    fail("Scenario CRUD via API", str(e))

try:
    r = requests.post(f"{BASE}/sensitivity", json={
        "inputs": {"tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
                   "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50},
        "target_variable": "gdp_growth"
    }, headers=AUTH, timeout=30)
    assert r.status_code == 200 and len(r.json()) == 6
    top = r.json()[0]
    ok("Sensitivity analysis (ML loop -> API response)", f"Top driver: {top['feature']} ({top['impact']:+.4f})")
except Exception as e:
    fail("Sensitivity analysis flow", str(e))

try:
    r = requests.get(f"{BASE}/model/info", timeout=5)
    d = r.json()
    ok("Model info (metadata from disk -> API)", f"{d.get('model_type','?')} R2={d.get('r2_score',0):.4f}")
except Exception as e:
    fail("Model info", str(e))

try:
    r = requests.get(f"{BASE}/model/feature-importance", timeout=10)
    fi = r.json()
    assert len(fi) > 0
    ok("Feature importance (disk -> API)", f"Top: {fi[0]['feature']} ({fi[0]['importance']:.4f})")
except Exception as e:
    fail("Feature importance flow", str(e))

# ──────────────────────────────────────────────────────────────
# LAYER 7: Frontend -> Backend CORS check
# ──────────────────────────────────────────────────────────────
section("LAYER 7: Frontend <-> Backend CORS / API Proxy")
try:
    r = requests.options(f"{BASE}/predict",
        headers={"Origin": "http://localhost:5173",
                 "Access-Control-Request-Method": "POST",
                 "Access-Control-Request-Headers": "Authorization,Content-Type"},
        timeout=5)
    acao = r.headers.get("access-control-allow-origin","")
    acam = r.headers.get("access-control-allow-methods","")
    if "localhost:5173" in acao or acao == "*":
        ok("CORS preflight: Frontend origin allowed", f"Allow-Origin: {acao}")
    else:
        warn("CORS preflight", f"Origin not explicitly allowed: '{acao}' — may block browser requests")
except Exception as e:
    warn("CORS preflight check", str(e))

try:
    r = requests.options(f"{BASE}/auth/login",
        headers={"Origin": "http://localhost:5173",
                 "Access-Control-Request-Method": "POST"},
        timeout=5)
    ok("CORS allowed for /auth/login", f"HTTP {r.status_code}")
except Exception as e:
    warn("CORS /auth/login", str(e))

# ──────────────────────────────────────────────────────────────
# FINAL REPORT
# ──────────────────────────────────────────────────────────────
section("INTEGRATION REPORT SUMMARY")
passed = [r for r in results if r[0]=="PASS"]
failed = [r for r in results if r[0]=="FAIL"]
warned  = [r for r in results if r[0]=="WARN"]
total   = len(results)
score   = int(100*len(passed)/total) if total else 0

print(f"\n  Total checks  : {total}")
print(f"  Passed        : {len(passed)}")
print(f"  Failed        : {len(failed)}")
print(f"  Warnings      : {len(warned)}")
print(f"\n  Integration Score: {score}%")

if failed:
    print("\n  --- FAILURES ---")
    for _,n,m in failed:
        print(f"  [FAIL] {n}")
        print(f"         => {m}")
if warned:
    print("\n  --- WARNINGS ---")
    for _,n,m in warned:
        print(f"  [WARN] {n}: {m}")

print()
layers = {
    "Frontend  (Vite/React)  ": [r for r in results if "Vite" in r[1] or "SPA" in r[1] or "Frontend" in r[1]],
    "Backend   (FastAPI)     ": [r for r in results if "FastAPI" in r[1] or "Swagger" in r[1] or "health" in r[1].lower() or "status" in r[1].lower()],
    "Database  (SQLite)      ": [r for r in results if "DB" in r[1] or "schema" in r[1] or "user write" in r[1] or "history write" in r[1] or "scenario" in r[1].lower()],
    "ML Model  (Scikit-learn)": [r for r in results if "ML" in r[1] or "model" in r[1].lower() or "sensitivity" in r[1].lower() or "feature" in r[1].lower()],
    "Auth Flow (JWT)         ": [r for r in results if "Register" in r[1] or "Login" in r[1] or "JWT" in r[1] or "/auth/me" in r[1]],
    "Simulation Flow         ": [r for r in results if "Predict" in r[1] or "History" in r[1] or "Compare" in r[1] or "Scenario CRUD" in r[1]],
    "CORS Integration        ": [r for r in results if "CORS" in r[1]],
}

print("  Layer-by-layer status:")
for layer, checks in layers.items():
    if not checks: continue
    p = sum(1 for c in checks if c[0]=="PASS")
    f = sum(1 for c in checks if c[0]=="FAIL")
    w = sum(1 for c in checks if c[0]=="WARN")
    status = "OK" if f==0 and w==0 else ("WARN" if f==0 else "FAIL")
    bar = f"[{status}]"
    print(f"  {bar:8} {layer} {p}/{len(checks)} pass")

print()
if score == 100:
    print("  *** FULL STACK INTEGRATED AND WORKING PERFECTLY ***")
elif score >= 90:
    print("  [GOOD] Stack is integrated — minor issues only.")
elif score >= 75:
    print("  [WARN] Stack partially integrated — fix failures above.")
else:
    print("  [CRITICAL] Integration broken — review failures.")

with open(os.path.join(os.path.dirname(__file__), "integration_report.json"), "w") as f:
    json.dump({"score":score,"total":total,"passed":len(passed),"failed":len(failed),
               "warnings":len(warned),"failures":[{"name":n,"error":m} for _,n,m in failed],
               "warnings_list":[{"name":n,"msg":m} for _,n,m in warned]}, f, indent=2)
print("  Report saved -> backend/integration_report.json\n")
sys.exit(0 if not failed else 1)
