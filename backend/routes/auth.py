"""Authentication Routes for PolicyAI."""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
import logging

from services.auth import (
    hash_password, verify_password, create_access_token, get_current_user
)
from services.database import (
    create_user, get_user_by_email, get_user_by_id, update_last_login
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


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


# --- Endpoints ---

@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
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
    user = get_user_by_email(req.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(req.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Update last login
    update_last_login(user['id'])

    token = create_access_token(user['id'], user['email'], user['name'])
    logger.info(f"User logged in: {user['email']}")
    return AuthResponse(
        token=token,
        user={"id": user['id'], "email": user['email'], "name": user['name']},
        message="Login successful"
    )


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
