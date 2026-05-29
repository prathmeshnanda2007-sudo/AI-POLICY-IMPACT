"""Authentication Routes for Nexora."""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
import logging

from services.auth import (
    hash_password, verify_password, create_access_token, get_current_user
)
from services.database import (
    create_user, get_user_by_email, get_user_by_id, update_last_login
)
from collections import defaultdict
import time
from fastapi import Request

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Simple In-Memory Rate Limiting for failed attempts (prevents brute force)
FAILED_ATTEMPTS = defaultdict(list)
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 10

def check_failed_attempts(email: str):
    """Raise 429 if too many recent failed attempts."""
    now = time.time()
    email = email.lower().strip()
    FAILED_ATTEMPTS[email] = [t for t in FAILED_ATTEMPTS[email] if now - t < LOCKOUT_MINUTES * 60]
    
    if len(FAILED_ATTEMPTS[email]) >= MAX_FAILED_ATTEMPTS:
        raise HTTPException(
            status_code=429, 
            detail=f"Too many failed login attempts. Please wait {LOCKOUT_MINUTES} minutes."
        )

def record_failed_attempt(email: str):
    """Record a failed attempt."""
    FAILED_ATTEMPTS[email.lower().strip()].append(time.time())

def clear_failed_attempts(email: str):
    """Clear failed attempts upon success."""
    FAILED_ATTEMPTS.pop(email.lower().strip(), None)


# --- Request/Response Schemas ---

class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    name: str = Field(min_length=2, max_length=100)


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: dict
    message: str


import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class GoogleLoginRequest(BaseModel):
    credential: str


# --- Endpoints ---

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=AuthResponse)
@limiter.limit("5/minute")
async def register(request: Request, req: RegisterRequest):
    """Register a new user account."""
    try:
        password_hash = hash_password(req.password)
        user = create_user(
            email=req.email,
            password_hash=password_hash,
            name=req.name
        )
        token = create_access_token(user['id'], user['email'], user['name'])
        logger.info(f"New user registered: {user['email']}")
        return AuthResponse(
            token=token,
            user={"id": user['id'], "email": user['email'], "name": user['name']},
            message="Account created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """Authenticate user and return JWT token."""
    check_failed_attempts(req.email)
    
    user = get_user_by_email(req.email)
    if user is None:
        record_failed_attempt(req.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(req.password, user['password_hash']):
        record_failed_attempt(req.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Success! Clear failed attempts
    clear_failed_attempts(req.email)

    # Update last login
    update_last_login(user['id'])

    token = create_access_token(user['id'], user['email'], user['name'])
    logger.info(f"User logged in: {user['email']}")
    return AuthResponse(
        token=token,
        user={"id": user['id'], "email": user['email'], "name": user['name']},
        message="Login successful"
    )


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")

@router.post("/google", response_model=AuthResponse)
@limiter.limit("5/minute")
async def google_login(request: Request, req: GoogleLoginRequest):
    """Authenticate user with Google OAuth token."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Client ID not configured")
        
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(req.credential, google_requests.Request(), GOOGLE_CLIENT_ID)
        
        email = idinfo.get("email")
        name = idinfo.get("name", "Google User")
        
        if not email:
            raise ValueError("Email not provided by Google")
            
        user = get_user_by_email(email)
        
        if user is None:
            # Create user
            user = create_user(
                email=email,
                password_hash="oauth:google",
                name=name
            )
            logger.info(f"New Google user registered: {email}")
        
        update_last_login(user['id'])
        
        token = create_access_token(user['id'], user['email'], user['name'])
        logger.info(f"Google User logged in: {user['email']}")
        
        return AuthResponse(
            token=token,
            user={"id": user['id'], "email": user['email'], "name": user['name']},
            message="Login successful"
        )
    except ValueError as e:
        logger.warning(f"Google login failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")
    except Exception as e:
        logger.error(f"Google Auth Error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user's profile."""
    user = get_user_by_id(current_user['id'])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user['id'],
        "email": user['email'],
        "name": user['name'],
        "created_at": user['created_at'],
    }


@router.post("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify that the current token is valid."""
    return {
        "valid": True,
        "user": current_user,
    }
