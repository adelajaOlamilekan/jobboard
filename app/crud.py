from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from . import models, schemas
from .config import settings

def create_user(db: Session, full_name: str, email: str, password_hash: str, role: str):
    user = models.User(full_name=full_name, email=email, password_hash=password_hash, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_email_token(db: Session, user_id):
    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES)
    et = models.EmailVerificationToken(token=token, user_id=user_id, expires_at=expires)
    db.add(et)
    db.commit()
    return et

def get_token(db: Session, token_str: str):
    return db.query(models.EmailVerificationToken).filter(models.EmailVerificationToken.token == token_str).first()

def delete_token(db: Session, token_str: str):
    db.query(models.EmailVerificationToken).filter(models.EmailVerificationToken.token == token_str).delete()
    db.commit()

# Jobs CRUD
def create_job(db: Session, user, title, description, location, status=None):
    job = models.Job(title=title, description=description, location=location, status=status or models.JobStatus.Draft, created_by=user.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def update_job(db: Session, job, **kwargs):
    for k,v in kwargs.items():
        setattr(job, k, v)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def delete_job(db: Session, job):
    db.delete(job)
    db.commit()

# Applications
def create_application(db: Session, applicant_id, job_id, resume_link, cover_letter):
    app = models.Application(applicant_id=applicant_id, job_id=job_id, resume_link=resume_link, cover_letter=cover_letter)
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

def get_application_by_applicant_job(db: Session, applicant_id, job_id):
    return db.query(models.Application).filter(models.Application.applicant_id==applicant_id, models.Application.job_id==job_id).first()
