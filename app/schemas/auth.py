# app/schemas/auth.py

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

from typing import Optional

from datetime import datetime


# =====================================================
# REGISTER
# =====================================================

class RegisterRequest(BaseModel):

    nama: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    login_identifier: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    login_type: str = Field(
        ...,
        examples=["Email", "Username"]
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128
    )

    umur: Optional[int] = None

    pekerjaan: Optional[str] = None


# =====================================================
# LOGIN
# =====================================================

class LoginRequest(BaseModel):

    login_identifier: str

    password: str


# =====================================================
# RESET PASSWORD
# =====================================================

class ResetPasswordRequest(BaseModel):

    login_identifier: str

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128
    )


# =====================================================
# USER RESPONSE
# =====================================================

class UserResponse(BaseModel):

    user_id: int

    nama: str

    login_identifier: str

    login_type: str

    umur: Optional[int] = None

    pekerjaan: Optional[str] = None

    created_at: Optional[datetime] = None


# =====================================================
# AUTH RESPONSE
# =====================================================

class AuthResponse(BaseModel):

    success: bool

    message: str

    user: Optional[UserResponse] = None


# =====================================================
# LOGIN RESPONSE
# =====================================================

class LoginResponse(BaseModel):

    success: bool

    message: str

    user: Optional[UserResponse] = None

    access_token: Optional[str] = None

    token_type: str = "bearer"