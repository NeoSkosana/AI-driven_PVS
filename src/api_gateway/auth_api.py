"""Authentication API endpoints."""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
import os
from dotenv import load_dotenv

from ..auth.auth_service import (
    Token,
    User,
    UserInDB,
    create_access_token,
    decode_token,
    verify_password,
)

load_dotenv()

# Configure authentication router with OpenAPI documentation
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Authentication failed"}}
)

# Update token URL to include /auth prefix
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# This would typically come from a database
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

def get_user(db, username: str) -> Optional[UserInDB]:
    """Get user from database."""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token_data = decode_token(token)
        if token_data.username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = get_user(fake_users_db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/token", 
    response_model=Token,
    summary="Create access token",
    description="Create a new access token using username and password",
    responses={
        200: {
            "description": "Successfully created access token",
            "model": Token
        },
        401: {
            "description": "Invalid credentials"
        }
    }
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """Login endpoint to get access token."""
    user = get_user(fake_users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", 
    response_model=User,
    summary="Get current user",
    description="Get information about the currently authenticated user",
    responses={
        200: {
            "description": "Current user information",
            "model": User
        }
    }
)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user information."""
    return current_user
