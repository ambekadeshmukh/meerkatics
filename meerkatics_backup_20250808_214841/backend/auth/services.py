# ========================================
# AUTHENTICATION SERVICE
# ========================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
import os
from typing import Optional, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 30
    
    def create_user(self, email: str, password: str, first_name: str, last_name: str, 
                   organization_name: Optional[str] = None) -> User:
        """Create a new user with optional organization"""
        
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.generate_verification_token()
        
        self.db.add(user)
        self.db.flush()  # Get user ID
        
        # Create organization if provided
        if organization_name:
            org = Organization(
                name=organization_name,
                slug=self._generate_org_slug(organization_name)
            )
            self.db.add(org)
            self.db.flush()  # Get org ID
            
            # Add user to organization as admin
            self._add_user_to_org(user.id, org.id, "org_admin")
        
        self.db.commit()
        
        # Send verification email
        self._send_verification_email(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user or not user.check_password(password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": str(user.id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        user = self.db.query(User).filter(User.verification_token == token).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        user.is_verified = True
        user.verification_token = None
        self.db.commit()
        
        return True
    
    def request_password_reset(self, email: str) -> bool:
        """Send password reset email"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists
            return True
        
        user.generate_reset_token()
        self.db.commit()
        
        # Send reset email
        self._send_password_reset_email(user)
        
        return True
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password with token"""
        user = self.db.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        self.db.commit()
        
        return True
    
    def _generate_org_slug(self, name: str) -> str:
        """Generate unique organization slug"""
        base_slug = name.lower().replace(" ", "-").replace("_", "-")
        base_slug = "".join(c for c in base_slug if c.isalnum() or c == "-")
        
        # Ensure uniqueness
        counter = 1
        slug = base_slug
        while self.db.query(Organization).filter(Organization.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def _add_user_to_org(self, user_id: int, org_id: int, role: str):
        """Add user to organization with role"""
        # This would use the association table
        from sqlalchemy import text
        self.db.execute(
            text("INSERT INTO user_organizations (user_id, organization_id, role) VALUES (:user_id, :org_id, :role)"),
            {"user_id": user_id, "org_id": org_id, "role": role}
        )
    
    def _send_verification_email(self, user: User):
        """Send email verification email"""
        # In production, use proper email service (SendGrid, SES, etc.)
        subject = "Verify your Meerkatics account"
        verify_url = f"https://app.meerkatics.com/verify?token={user.verification_token}"
        
        body = f"""
        Hi {user.first_name},
        
        Welcome to Meerkatics! Please verify your email address by clicking the link below:
        
        {verify_url}
        
        If you didn't create this account, please ignore this email.
        
        Best regards,
        The Meerkatics Team
        """
        
        self._send_email(user.email, subject, body)
    
    def _send_password_reset_email(self, user: User):
        """Send password reset email"""
        subject = "Reset your Meerkatics password"
        reset_url = f"https://app.meerkatics.com/reset-password?token={user.reset_token}"
        
        body = f"""
        Hi {user.first_name},
        
        You requested a password reset for your Meerkatics account. Click the link below to reset your password:
        
        {reset_url}
        
        This link will expire in 1 hour. If you didn't request this reset, please ignore this email.
        
        Best regards,
        The Meerkatics Team
        """
        
        self._send_email(user.email, subject, body)
    
    def _send_email(self, to_email: str, subject: str, body: str):
        """Send email using SMTP"""
        # In production, replace with proper email service
        try:
            smtp_server = os.getenv("SMTP_SERVER", "localhost")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            from_email = os.getenv("FROM_EMAIL", "noreply@meerkatics.com")
            
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            # In production, log this properly
