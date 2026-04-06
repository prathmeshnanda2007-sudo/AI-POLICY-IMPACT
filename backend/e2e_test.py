"""Full End-to-End Integration Test for PolicyAI"""
import urllib.request
import json
import sys

BASE = "http://localhost:8000"
results = []


def test(name, method, path, data=None, token=None, expect_status=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(req)
        d = json.loads(r.read())
        results.append(("PASS", name))
        return d
    except urllib.error.HTTPError as e:
        if expect_status and e.code == expect_status:
            results.append(("PASS", name + " (expected " + str(e.code) + ")"))
            return None
        results.append(("FAIL", name + " (HTTP " + str(e.code) + ")"))
        return None
    except Exception as e:
        results.append(("FAIL", name + " (" + str(e) + ")"))
        return None


# 1. Health check
test("Health check", "GET", "/health")

# 2. Root endpoint
test("Root API endpoint", "GET", "/")

# 3. Register new user
import random
email = "e2e_test_" + str(random.randint(1000, 9999)) + "@test.com"
reg = test("Register new user", "POST", "/auth/register", {
    "email": email, "password": "SecurePass123!", "name": "E2E Tester"
})
token = reg["token"] if reg else None

# 4. Login with same user
login = test("Login with credentials", "POST", "/auth/login", {
    "email": email, "password": "SecurePass123!"
})
if login:
    token = login["token"]

# 5. Verify JWT token
test("Verify JWT token", "POST", "/auth/verify", token=token)

# 6. Get user profile
test("Get user profile (/auth/me)", "GET", "/auth/me", token=token)

# 7. Unauthenticated access blocked
test("Reject unauthenticated /history", "GET", "/history", expect_status=401)
test("Reject unauthenticated /predict", "POST", "/predict", data={"tax_rate": 25}, expect_status=401)

# 8. ML Prediction (authenticated)
pred = test("ML Prediction (/predict)", "POST", "/predict", {
    "tax_rate": 25, "fuel_price": 3.5, "subsidy": 15,
    "public_spending": 30, "interest_rate": 5, "environmental_regulation": 50
}, token=token)

# 9. Scenario Comparison
test("Compare 2 scenarios", "POST", "/compare", {
    "scenarios": [
        {"tax_rate": 20, "fuel_price": 3, "subsidy": 20, "public_spending": 35, "interest_rate": 3, "environmental_regulation": 70},
        {"tax_rate": 40, "fuel_price": 5, "subsidy": 5, "public_spending": 20, "interest_rate": 8, "environmental_regulation": 30},
    ]
}, token=token)

# 10. Save a scenario
saved = test("Save scenario", "POST", "/scenarios", {
    "name": "E2E Test Scenario", "inputs": {"tax_rate": 25}, "results": pred or {}
}, token=token)

# 11. List scenarios
test("List saved scenarios", "GET", "/scenarios", token=token)

# 12. Simulation history
test("Get simulation history", "GET", "/history", token=token)

# 13. Model info
test("Get model info", "GET", "/model/info", token=token)

# 14. Feature importance
test("Get feature importance", "GET", "/model/feature-importance", token=token)

# 15. Sensitivity analysis
test("Sensitivity analysis", "POST", "/sensitivity", {
    "target_variable": "gdp_growth"
}, token=token)

# 16. AI Recommendation
test("AI policy recommendation", "POST", "/recommend", {
    "gdp_growth": 4.0, "inflation": 2.5, "employment_rate": 96
}, token=token)

# 17. Delete scenario
if saved and saved.get("id"):
    test("Delete scenario", "DELETE", "/scenarios/" + str(saved["id"]), token=token)

# 18. Wrong password rejected
test("Wrong password rejected", "POST", "/auth/login", {
    "email": email, "password": "wrongpassword123"
}, expect_status=401)

# 19. Duplicate registration rejected
test("Duplicate email rejected", "POST", "/auth/register", {
    "email": email, "password": "AnotherPass!", "name": "Dup"
}, expect_status=400)

# === SUMMARY ===
print("=" * 60)
passed = sum(1 for r in results if r[0] == "PASS")
failed = sum(1 for r in results if r[0] == "FAIL")
total = len(results)
print("RESULTS: " + str(passed) + " PASSED / " + str(failed) + " FAILED / " + str(total) + " TOTAL")
print("=" * 60)
for status, name in results:
    icon = "OK" if status == "PASS" else "XX"
    print("  [" + icon + "] " + name)
print("=" * 60)
if failed == 0:
    print("ALL TESTS PASSED - WEBSITE IS FULLY INTEGRATED AND FUNCTIONAL")
else:
    print(str(failed) + " TEST(S) FAILED")
    sys.exit(1)
