# Meerkatics Authentication API Routes
# Complete FastAPI routes for authentication, user management, and API keys

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
import json

# Import our authentication models and services
from .auth_system import (
    User, Organization, Project, APIKey, AuditLog,
    AuthService, APIKeyService, RBACService, AuthMiddleware, rate_limiter
)

# ========================================
# PYDANTIC MODELS (REQUEST/RESPONSE)
# ========================================

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    organization_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    organizations: List[dict] = []
    
    class Config:
        from_attributes = True

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class APIKeyCreate(BaseModel):
    name: str
    scopes: List[str]
    project_id: Optional[int] = None
    expires_in_days: Optional[int] = None
    rate_limit_requests_per_hour: Optional[int] = 1000
    rate_limit_data_per_day: Optional[int] = 10000

class APIKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    scopes: List[str]
    project_id: Optional[int]
    is_active: bool
    rate_limit_requests_per_hour: int
    rate_limit_data_per_day: int
    last_used: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class APIKeyCreatedResponse(BaseModel):
    api_key: APIKeyResponse
    key: str  # Only returned once during creation

class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    plan: str
    monthly_budget: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserInvite(BaseModel):
    email: EmailStr
    role: str
    
    @validator('role')
    def validate_role(cls, v):
        valid_roles = ["org_admin", "developer", "viewer", "billing"]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v

class UserRoleChange(BaseModel):
    role: str
    
    @validator('role')
    def validate_role(cls, v):
        valid_roles = ["org_admin", "developer", "viewer", "billing"]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v

# ========================================
# DEPENDENCY INJECTION
# ========================================

def get_db():
    """Get database session - implement based on your database setup"""
    # This should return your SQLAlchemy session
    # Example:
    # from .database import SessionLocal
    # db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()
    pass

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_api_key_service(db: Session = Depends(get_db)) -> APIKeyService:
    return APIKeyService(db)

def get_rbac_service(db: Session = Depends(get_db)) -> RBACService:
    return RBACService(db)

def get_auth_middleware(db: Session = Depends(get_db)) -> AuthMiddleware:
    return AuthMiddleware(db)
