from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .. import schemas, crud, auth as auth_lib
from ..db import get_db
from ..email_utils import send_email_background
from ..config import settings
from ..models import RoleEnum

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup", response_model=schemas.BaseResponse)
def signup(payload: schemas.SignupIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # uniqueness
    existing = crud.get_user_by_email(db, payload.email)
    if existing:
        return {"success": False, "message": "Email already exists", "object": None, "errors": ["email already exists"]}
    password_hash = auth_lib.hash_password(payload.password)
    user = crud.create_user(db, payload.full_name, payload.email, password_hash, payload.role)
    token = crud.create_email_token(db, user.id)

    # send verification email
    # verify_link = f"{settings.FRONTEND_BASE_URL}/api/verify-email?token={token.token}"
    html = f"<p>Hi {user.full_name}, here is your verification token {token.token}. Token expires in {settings.VERIFICATION_TOKEN_EXPIRE_MINUTES} minutes.</p>"
    send_email_background(background_tasks, user.email, "Verify your email", html)
    respone_data = {"success": True, "message": "Registered successfully. Verification email sent.", "object": {"user_id": str(user.id)}, "errors": None}
    return JSONResponse(content=respone_data, status_code=status.HTTP_201_CREATED)

@router.get("/verify-email", response_model=schemas.BaseResponse)
def verify_email(token: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    record = crud.get_token(db, token)
    if not record:
        return {"success": False, "message":"Token invalid or malformed", "object": None, "errors": ["invalid token"]}
    from datetime import datetime
    if record.expires_at < datetime.utcnow():
        # token expired -> generate new token and send email
        new_token = crud.create_email_token(db, record.user_id)
        user = db.query(models.User).filter(models.User.id == record.user_id).first()
        link = f"{settings.FRONTEND_BASE_URL}/api/verify-email?token={new_token.token}"
        html = f"<p>Your verification link expired. Click <a href='{link}'>here</a> to verify.</p>"
        send_email_background(background_tasks, user.email, "New verification link", html)
        # delete old token
        crud.delete_token(db, token)
        return {"success": False, "message": "Token expired. A new verification email was sent.", "object": None, "errors": ["token expired - new email sent"]}
    # token valid
    user = db.query(models.User).filter(models.User.id == record.user_id).first()
    if user.is_verified:
        return {"success": True, "message": "Email already verified", "object": {"user_id": str(user.id)}, "errors": None}
    user.is_verified = 1
    db.add(user)
    db.commit()
    crud.delete_token(db, token)
    return {"success": True, "message": "Email verified successfully", "object": {"user_id": str(user.id)}, "errors": None}

@router.post("/login", response_model=schemas.BaseResponse)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user:
        return {"success": False, "message":"Invalid credentials", "object": None, "errors":["invalid credentials"]}
    if not auth_lib.verify_password(payload.password, user.password_hash):
        return {"success": False, "message":"Invalid credentials", "object": None, "errors":["invalid credentials"]}
    # create JWT
    token = auth_lib.create_access_token({"user_id": str(user.id), "role": user.role.value})
    return {"success": True, "message":"Login successful", "object":{"access_token": token, "token_type":"bearer"}, "errors": None}
