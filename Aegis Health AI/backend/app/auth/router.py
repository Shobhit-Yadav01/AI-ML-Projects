import os
import json
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from backend.app.config import settings
from backend.app.models.auth import UserRegister, UserLogin, Token, TokenData
from backend.app.auth.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "users_db.json")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login-form-compat")

def load_users() -> dict:
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users: dict):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"Failed to write to local user db: {e}")

@router.post("/register", response_model=dict)
async def register(user_data: UserRegister):
    users = load_users()
    if user_data.email in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    
    users[user_data.email] = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": get_password_hash(user_data.password)
    }
    save_users(users)
    return {"message": "Registration successful!", "email": user_data.email}

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    users = load_users()
    user = users.get(credentials.email)
    
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user["email"], expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
        "email": user["email"]
    }

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    users = load_users()
    user = users.get(token_data.email)
    if user is None:
        raise credentials_exception
    return {
        "username": user["username"],
        "email": user["email"]
    }

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
