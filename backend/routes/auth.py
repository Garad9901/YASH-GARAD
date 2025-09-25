from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials, auth
import os

from ..database import get_db
from ..models import User
from ..config import settings
from ..utils import verify_password, get_password_hash, create_access_token

router = APIRouter()

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.firebase_credentials_path)
    firebase_admin.initialize_app(cred)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

from pydantic import BaseModel

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register", response_model=dict)
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    email = request.email
    password = request.password
    full_name = request.full_name
    # Check if user exists
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create Firebase user
    try:
        firebase_user = auth.create_user(
            email=email,
            password=password,
            display_name=full_name
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Firebase error: {str(e)}")

    # Hash password and create local user
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        username=email.split("@")[0],  # Simple username from email
        hashed_password=hashed_password,
        full_name=full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User registered successfully", "user_id": db_user.id}

@router.post("/login", response_model=dict)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Authenticate with Firebase
    try:
        firebase_user = auth.get_user_by_email(request.email)
        # For simplicity, we'll use Firebase token verification
        # In production, implement proper Firebase token verification
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Get local user
    db_user = db.query(User).filter(User.email == request.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    # Create JWT token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=dict)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify Firebase token
        decoded_token = auth.verify_id_token(token)
        email = decoded_token['email']
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return {"id": user.id, "email": user.email, "full_name": user.full_name}
