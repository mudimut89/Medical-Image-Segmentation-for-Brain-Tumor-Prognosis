"""
Authentication system for Brain Tumor Segmentation
Simple user registration and login functionality
"""

import json
import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, EmailStr
import jwt

# Simple in-memory user store (for demo purposes)
USERS_DB = Path("objective3_interface/backend/users.json")
SESSIONS_DB = Path("objective3_interface/backend/sessions.json")

class User(BaseModel):
    email: EmailStr
    password_hash: str
    full_name: str
    created_at: datetime
    is_active: bool = True

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    token: Optional[str] = None
    user_data: Optional[Dict] = None

# JWT Secret (in production, use environment variable)
JWT_SECRET = "brain-tumor-segmentation-secret-key-2024"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def create_jwt_token(user_id: str, email: str) -> str:
    """Create JWT token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Optional[Dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

def load_users() -> Dict[str, User]:
    """Load users from file"""
    if not USERS_DB.exists():
        return {}
    
    try:
        with open(USERS_DB, 'r') as f:
            data = json.load(f)
            return {user_id: User(**user_data) for user_id, user_data in data.items()}
    except Exception:
        return {}

def save_users(users: Dict[str, User]):
    """Save users to file"""
    USERS_DB.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_DB, 'w') as f:
        json.dump({user_id: user.dict() for user_id, user in users.items()}, f, indent=2, default=str)

def register_user(registration: UserRegistration) -> AuthResponse:
    """Register new user"""
    users = load_users()
    
    # Check if user already exists
    for user_id, user in users.items():
        if user.email == registration.email:
            return AuthResponse(
                success=False,
                message="Email already registered. Please login instead."
            )
    
    # Create new user
    user_id = str(uuid.uuid4())
    password_hash = hash_password(registration.password)
    
    new_user = User(
        email=registration.email,
        password_hash=password_hash,
        full_name=registration.full_name,
        created_at=datetime.utcnow()
    )
    
    users[user_id] = new_user
    save_users(users)
    
    # Create token
    token = create_jwt_token(user_id, new_user.email)
    
    return AuthResponse(
        success=True,
        message="Registration successful! Welcome to Brain Tumor Analysis System.",
        user_id=user_id,
        token=token,
        user_data={
            "user_id": user_id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "created_at": new_user.created_at.isoformat()
        }
    )

def login_user(login: UserLogin) -> AuthResponse:
    """Login user"""
    users = load_users()
    
    # Find user by email
    for user_id, user in users.items():
        if user.email == login.email:
            if verify_password(login.password, user.password_hash):
                if not user.is_active:
                    return AuthResponse(
                        success=False,
                        message="Account is deactivated. Please contact support."
                    )
                
                # Create token
                token = create_jwt_token(user_id, user.email)
                
                return AuthResponse(
                    success=True,
                    message="Login successful! Welcome back.",
                    user_id=user_id,
                    token=token,
                    user_data={
                        "user_id": user_id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "created_at": user.created_at.isoformat()
                    }
                )
            else:
                return AuthResponse(
                    success=False,
                    message="Invalid password. Please try again."
                )
    
    return AuthResponse(
        success=False,
        message="Email not found. Please register first."
    )

def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID"""
    users = load_users()
    return users.get(user_id)

def get_user_by_token(token: str) -> Optional[User]:
    """Get user by JWT token"""
    payload = verify_jwt_token(token)
    if not payload:
        return None
    
    return get_user_by_id(payload["user_id"])
