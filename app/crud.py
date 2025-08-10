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


