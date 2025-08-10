from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class BaseResponse(BaseModel):
    success: bool
    message: str
    object: Optional[dict] = None
    errors: Optional[List[str]] = None

class PaginatedResponse(BaseModel):
    success: bool
    message: str
    object: List[dict]
    pageNumber: int
    pageSize: int
    totalSize: int
    errors: Optional[List[str]] = None

# input schemas
class SignupIn(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=200)
    email: EmailStr
    password: str
    role: str

    @field_validator("full_name")
    def name_must_be_two_parts(cls, v):
        parts = v.strip().split(" ")
        if len(parts) != 2 or not all(p.isalpha() for p in parts):
            raise ValueError("Full name must contain only alphabets and exactly one space between first and last name")
        return v

    @field_validator("password")
    def strong_pwd(cls, v):
        import re
        if len(v) < 8: raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v): raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", v): raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"[0-9]", v): raise ValueError("Password must contain a digit")
        if not re.search(r"\W", v): raise ValueError("Password must contain a special character")
        return v

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=20, max_length=2000)
    location: Optional[str] = None
    status: Optional[str] = None

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    location: Optional[str] = None
    status: Optional[str] = None

class ApplicationCreate(BaseModel):
    cover_letter: Optional[str] = Field(None, max_length=200)

class ApplicationStatusUpdate(BaseModel):
    new_status: str

# response schemas (simplified)
class JobOut(BaseModel):
    id: UUID
    title: str
    description: str
    location: Optional[str]
    status: str
    created_by: UUID
    created_at: datetime

class ApplicationOut(BaseModel):
    id: UUID
    job_id: UUID
    applicant_id: UUID
    resume_link: str
    cover_letter: Optional[str]
    status: str
    applied_at: datetime
