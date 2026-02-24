"""
User Schemas - Request/Response models for authentication and user management
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


# ==========================================
# Authentication Schemas
# ==========================================

class LoginRequest(BaseModel):
    """Login request body."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginResponse(BaseModel):
    """Login response with JWT token."""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: int  # user_id
    role: UserRole
    exp: datetime


# ==========================================
# User Base Schemas
# ==========================================

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=6)
    role: UserRole


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    role: UserRole
    profile_picture: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update schema (partial)."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class UserStatusUpdate(BaseModel):
    """Schema for activating/deactivating users."""
    is_active: bool


# ==========================================
# Student Registration
# ==========================================

class StudentRegister(BaseModel):
    """Student registration request."""
    # User fields
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    
    # Student-specific fields
    roll_number: str = Field(..., min_length=1, max_length=50)
    degree_id: int
    department_id: int
    semester_id: int
    passout_year: int = Field(..., ge=2020, le=2040)
    admission_year: int = Field(..., ge=2015, le=2030)


class StudentProfileResponse(BaseModel):
    """Student profile response."""
    id: int
    user: UserResponse
    roll_number: str
    degree_id: int
    department_id: int
    current_semester_id: int
    passout_year: int
    admission_year: int

    class Config:
        from_attributes = True


# ==========================================
# Teacher Registration
# ==========================================

class TeacherRegister(BaseModel):
    """Teacher registration request (by admin)."""
    # User fields
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    
    # Teacher-specific fields
    employee_id: str = Field(..., min_length=1, max_length=50)
    department_id: int
    designation: Optional[str] = Field(None, max_length=100)


class TeacherProfileResponse(BaseModel):
    """Teacher profile response."""
    id: int
    user: UserResponse
    employee_id: str
    department_id: int
    designation: Optional[str]

    class Config:
        from_attributes = True


# Forward references
LoginResponse.model_rebuild()
