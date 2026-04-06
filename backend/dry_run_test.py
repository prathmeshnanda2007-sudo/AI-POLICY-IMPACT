"""
Comprehensive Dry Run Test for AI Policy Impact Simulator
Tests: Backend API, ML Model, Database, and all endpoints
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json
import time

BASE = 'http://localhost:8000'
errors = []
passed = []

def test(name, fn):
    try:
        fn()
        passed.append(name)
        print(f'  [PASS]')
    except Exception as e:
        errors.append((name, str(e)))
        print(f'  [FAIL]: {e}')

# === 1. HEALTH & ROOT ===
print('='*60)
print('SECTION 1: Server Health')
print('='*60)

print('\n[1] Health Check')
def t1():
    r = requests.get(f'{BASE}/health', timeout=5)
    assert r.status_code == 200, f'Status {r.status_code}'
    assert r.json()['status'] == 'healthy'
    print(f'      Response: {r.json()}')
test('health', t1)

print('\n[2] Root Endpoint')
def t2():
    r = requests.get(f'{BASE}/', timeout=5)
    assert r.status_code == 200
    d = r.json()
    assert d['status'] == 'online'
    print(f'      API: {d["name"]} v{d["version"]}')
test('root', t2)

# === 2. ML MODEL ===
print('\n' + '='*60)
print('SECTION 2: ML Model')
print('='*60)

print('\n[3] Model Info')
def t3():
    r = requests.get(f'{BASE}/model/info', timeout=5)
    assert r.status_code == 200
    d = r.json()
    print(f'      Model: {d.get("model_type")}')
    print(f'      R2: {d.get("r2_score")}')
    print(f'      RMSE: {d.get("rmse")}')
    print(f'      Samples: {d.get("training_samples")}')
test('model_info', t3)

print('\n[4] Feature Importance')
def t4():
    r = requests.get(f'{BASE}/model/feature-importance', timeout=5)
    assert r.status_code == 200
    d = r.json()
    assert len(d) == 6, f'Expected 6 features, got {len(d)}'
    for f in d:
        print(f'      {f["feature"]}: {f["importance"]:.4f}')
test('feature_importance', t4)

# === 3. PREDICTIONS ===
print('\n' + '='*60)
print('SECTION 3: Predictions')
print('='*60)

print('\n[5] Predict -- Default Inputs')
def t5():
    payload = {'tax_rate':25, 'fuel_price':3.5, 'subsidy':15, 'public_spending':30, 'interest_rate':5, 'environmental_regulation':50}
    r = requests.post(f'{BASE}/predict', json=payload, timeout=10)
    assert r.status_code == 200
    d = r.json()
    for k in ['gdp_growth','inflation','employment_rate','environment_score','public_satisfaction','confidence']:
        assert k in d, f'Missing key: {k}'
        print(f'      {k}: {d[k]:.4f}')
test('predict_default', t5)

print('\n[6] Predict -- High Tax + Low Subsidy (Stress)')
def t6():
    payload = {'tax_rate':55, 'fuel_price':8.0, 'subsidy':2, 'public_spending':50, 'interest_rate':15, 'environmental_regulation':10}
    r = requests.post(f'{BASE}/predict', json=payload, timeout=10)
    assert r.status_code == 200
    d = r.json()
    assert d['gdp_growth'] < 0, f'Expected negative GDP, got {d["gdp_growth"]}'
    print(f'      GDP: {d["gdp_growth"]:.4f} (negative = correct for stress scenario)')
    print(f'      Inflation: {d["inflation"]:.4f}')
    print(f'      Employment: {d["employment_rate"]:.4f}')
test('predict_stress', t6)

print('\n[7] Predict -- Green Policy (Low Tax + High Regulation)')
def t7():
    payload = {'tax_rate':10, 'fuel_price':2.0, 'subsidy':40, 'public_spending':20, 'interest_rate':2, 'environmental_regulation':90}
    r = requests.post(f'{BASE}/predict', json=payload, timeout=10)
    assert r.status_code == 200
    d = r.json()
    assert d['environment_score'] > 50, f'Expected env>50, got {d["environment_score"]}'
    assert d['gdp_growth'] > 0, f'Expected positive GDP for green policy'
    print(f'      GDP: {d["gdp_growth"]:.4f}')
    print(f'      Environment: {d["environment_score"]:.4f} (high = correct for green policy)')
    print(f'      Satisfaction: {d["public_satisfaction"]:.4f}')
test('predict_green', t7)

print('\n[8] Predict -- Validation Error (out of range)')
def t8():
    payload = {'tax_rate':999, 'fuel_price':3.5, 'subsidy':15, 'public_spending':30, 'interest_rate':5, 'environmental_regulation':50}
    r = requests.post(f'{BASE}/predict', json=payload, timeout=10)
    assert r.status_code == 422, f'Expected 422, got {r.status_code}'
    print(f'      Correctly rejected with 422 validation error')
test('validation', t8)

# === 4. COMPARE ===
print('\n' + '='*60)
print('SECTION 4: Scenario Comparison')
print('='*60)

print('\n[9] Compare 2 Scenarios')
def t9():
    scenarios = [
        {'tax_rate':25, 'fuel_price':3.5, 'subsidy':15, 'public_spending':30, 'interest_rate':5, 'environmental_regulation':50},
        {'tax_rate':10, 'fuel_price':2.0, 'subsidy':40, 'public_spending':20, 'interest_rate':2, 'environmental_regulation':90},
    ]
    r = requests.post(f'{BASE}/compare', json={'scenarios': scenarios}, timeout=10)
    assert r.status_code == 200
    d = r.json()
    assert len(d) == 2
    print(f'      Scenario 1 GDP: {d[0]["gdp_growth"]:.4f}')
    print(f'      Scenario 2 GDP: {d[1]["gdp_growth"]:.4f}')
    print(f'      Delta: {d[1]["gdp_growth"] - d[0]["gdp_growth"]:.4f}')
test('compare', t9)

# === 5. DATABASE / SCENARIOS ===
print('\n' + '='*60)
print('SECTION 5: Database & Scenarios')
print('='*60)

saved_id = None

print('\n[10] Save Scenario')
def t10():
    global saved_id
    payload = {
        'name': 'DryRun Test Scenario',
        'inputs': {'tax_rate':25, 'fuel_price':3.5, 'subsidy':15, 'public_spending':30, 'interest_rate':5, 'environmental_regulation':50},
        'results': {'gdp_growth':2.1, 'inflation':3.5, 'employment_rate':94.2, 'environment_score':55, 'public_satisfaction':65}
    }
    r = requests.post(f'{BASE}/scenarios', json=payload, timeout=5)
    assert r.status_code == 200
    d = r.json()
    saved_id = d['id']
    print(f'      Saved id={saved_id}, name="{d["name"]}"')
test('save_scenario', t10)

print('\n[11] List Scenarios')
def t11():
    r = requests.get(f'{BASE}/scenarios', timeout=5)
    assert r.status_code == 200
    d = r.json()
    assert len(d) >= 1, f'Expected >=1 scenario, got {len(d)}'
    print(f'      Found {len(d)} scenarios:')
    for s in d:
        print(f'        id={s["id"]}, name="{s["name"]}"')
test('list_scenarios', t11)

print('\n[12] Delete Scenario')
def t12():
    r = requests.delete(f'{BASE}/scenarios/{saved_id}', timeout=5)
    assert r.status_code == 200
    print(f'      Deleted scenario {saved_id}')
    # Verify deleted
    r2 = requests.get(f'{BASE}/scenarios', timeout=5)
    remaining = [s for s in r2.json() if s['id'] == saved_id]
    assert len(remaining) == 0, f'Scenario still exists after deletion!'
    print(f'      Verified: no longer in list')
test('delete_scenario', t12)

# === 6. HISTORY ===
print('\n' + '='*60)
print('SECTION 6: Simulation History')
print('='*60)

print('\n[13] Get History')
def t13():
    r = requests.get(f'{BASE}/history', timeout=5)
    assert r.status_code == 200
    d = r.json()
    assert len(d) >= 3, f'Expected >=3 history entries (from predictions above), got {len(d)}'
    print(f'      Found {len(d)} history entries')
    for h in d[:3]:
        print(f'        id={h["id"]}, gdp={h["results"]["gdp_growth"]:.3f}, ts={h["timestamp"]}')
test('history', t13)

# === 7. ADVANCED ML ===
print('\n' + '='*60)
print('SECTION 7: Advanced ML Features')
print('='*60)

print('\n[14] Sensitivity Analysis')
def t14():
    payload = {
        'inputs': {'tax_rate':25, 'fuel_price':3.5, 'subsidy':15, 'public_spending':30, 'interest_rate':5, 'environmental_regulation':50},
        'target_variable': 'gdp_growth'
    }
    r = requests.post(f'{BASE}/sensitivity', json=payload, timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert len(d) == 6
    print(f'      Sensitivity on GDP Growth:')
    for s in d:
        print(f'        {s["feature"]}: impact={s["impact"]:.4f} ({s["direction"]})')
test('sensitivity', t14)

print('\n[15] AI Recommendation')
def t15():
    payload = {'gdp_growth':4.0, 'inflation':2.5, 'employment_rate':96, 'environment_score':80}
    r = requests.post(f'{BASE}/recommend', json=payload, timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert 'recommended_inputs' in d
    assert 'predicted_outcomes' in d
    print(f'      Recommended Policy:')
    for k,v in d['recommended_inputs'].items():
        print(f'        {k}: {v}')
    print(f'      Expected Outcomes:')
    for k,v in d['predicted_outcomes'].items():
        print(f'        {k}: {v}')
test('recommend', t15)

# === SUMMARY ===
print('\n' + '='*60)
print(f'DRY RUN RESULTS: {len(passed)}/{len(passed)+len(errors)} PASSED')
print('='*60)
if errors:
    print('\nFAILURES:')
    for name, err in errors:
        print(f'  [FAIL] {name}: {err}')
else:
    print('\n*** ALL 15 TESTS PASSED -- APP IS FULLY FUNCTIONAL! ***')
print('='*60)
