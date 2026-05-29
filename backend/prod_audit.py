import os
import sys
from urllib.parse import urlparse

def check_prod_readiness():
    print("=== BACKEND PRODUCTION READINESS AUDIT ===")
    issues = []
    warnings = []
    
    # 1. Environment Variables
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    has_env = os.path.exists(env_file)
    if not has_env:
        warnings.append(".env file is missing. Using system environment variables?")
    
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
    
    from services.auth import JWT_SECRET
    if "dev" in JWT_SECRET.lower() or "change" in JWT_SECRET.lower():
        issues.append("[SECURITY] JWT_SECRET is using the hardcoded development default! This is highly insecure for production.")
    
    # 2. Database Connection
    from services.database import engine
    db_url = str(engine.url)
    if "localhost" in db_url or "sqlite" in db_url:
        issues.append(f"[DATABASE] Database is using local/sqlite instead of a cloud instance: {db_url}")
    else:
        print(f"[SUCCESS] Database is pointing to cloud instance ({db_url.split('@')[-1]})")
        
    if "sslmode=require" not in db_url and "neon.tech" in db_url:
        warnings.append("[DATABASE] NeonDB URL might be missing sslmode=require")

    # 3. Main.py Configuration
    main_py_path = os.path.join(os.path.dirname(__file__), "main.py")
    with open(main_py_path, 'r', encoding='utf-8') as f:
        main_content = f.read()
        
    if "reload=True" in main_content:
        warnings.append("[SERVER] uvicorn.run() has reload=True. This should be removed or disabled in production.")
        
    if 'allow_origins=["*"]' in main_content and 'ENVIRONMENT == "production"' in main_content:
        # Check how CORS is configured
        pass

    # 4. Frontend static files
    dist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")
    if not os.path.exists(dist_dir):
        issues.append("[FRONTEND] dist/ folder is missing. The FastAPI server won't be able to serve the frontend.")
    else:
        print("[SUCCESS] Frontend dist/ folder exists.")

    print("\n--- AUDIT RESULTS ---")
    if issues:
        print("CRITICAL ISSUES:")
        for i in issues:
            print(f"  [FAIL] {i}")
    else:
        print("[SUCCESS] No critical issues found.")
        
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  [WARN] {w}")
            
    if not issues and not warnings:
        print("\n[SUCCESS] Backend is completely PRODUCTION READY!")

if __name__ == '__main__':
    check_prod_readiness()
