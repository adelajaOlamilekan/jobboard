import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .db import Base
import enum

class RoleEnum(str, enum.Enum):
    applicant = "applicant"
    company = "company"

class JobStatus(str, enum.Enum):
    Draft = "Draft"
    Open = "Open"
    Closed = "Closed"

class ApplicationStatus(str, enum.Enum):
    Applied = "Applied"
    Reviewed = "Reviewed"
    Interview = "Interview"
    Rejected = "Rejected"
    Hired = "Hired"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(200), nullable=False)
    email = Column(String(256), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    is_verified = Column(Integer, default=0)  # 0 false, 1 true
    created_at = Column(DateTime, default=func.now())

    jobs = relationship("Job", back_populates="owner")
    applications = relationship("Application", back_populates="applicant")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(200))
    status = Column(Enum(JobStatus), default=JobStatus.Draft)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    owner = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    resume_link = Column(String(1024), nullable=False)
    cover_letter = Column(String(200))
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.Applied)
    applied_at = Column(DateTime, default=func.now())

    applicant = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")

class EmailVerificationToken(Base):
    __tablename__ = "email_tokens"
    token = Column(String(128), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
