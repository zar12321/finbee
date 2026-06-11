# app/schemas/profile.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


# =====================================================
# PROFILE RESPONSE
# =====================================================

class ProfileResponse(BaseModel):

    user_id: int

    nama: str

    login_identifier: str

    login_type: str

    umur: Optional[int] = None

    pekerjaan: Optional[str] = None

    created_at: Optional[datetime] = None


# =====================================================
# UPDATE PROFILE REQUEST
# =====================================================

class ProfileUpdateRequest(BaseModel):

    nama: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    umur: Optional[int] = Field(
        default=None,
        ge=0,
        le=120
    )

    pekerjaan: Optional[str] = Field(
        default=None,
        max_length=100
    )


# =====================================================
# CHANGE PASSWORD REQUEST
# =====================================================

class ChangePasswordRequest(BaseModel):

    current_password: str

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128
    )


# =====================================================
# PROFILE RESPONSE MESSAGE
# =====================================================

class ProfileUpdateResponse(BaseModel):

    success: bool

    message: str

    profile: Optional[ProfileResponse] = None