from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks, Query, status
from sqlalchemy.orm import Session
from ..db import get_db
from .. import crud, auth as auth_lib, models
from ..schemas import BaseResponse, PaginatedResponse
from ..cloudinary_utils import upload_resume_file
from ..email_utils import send_email_background
from ..config import settings
import sqlalchemy
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/applications", tags=["applications"])

# apply for job (applicant only)
@router.post("/jobs/{job_id}/apply", response_model=BaseResponse)
def apply_job(job_id: str, cover_letter: str = None, resume: UploadFile = File(...), background_tasks: BackgroundTasks = None,
              db: Session = Depends(get_db), current_user = Depends(auth_lib.require_role("applicant"))):
    # check job exists
    try:
        job = crud.get_job(db, job_id)
    except sqlalchemy.exc.DataError:
        response_data = {"success": False, "message":"Job not found", "object": None, "errors": ["not found"]}
        return JSONResponse(content=response_data, status_code=status.HTTP_404_NOT_FOUND)
    if not job:
        return {"success": False, "message":"Job not found", "object": None, "errors": ["not found"]}
    # duplicate check
    existing = crud.get_application_by_applicant_job(db, current_user.id, job.id)
    if existing:
        return {"success": False, "message":"Already applied", "object": None, "errors": ["duplicate application"]}
    # validate resume mime/type and extension
    allowed = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if resume.content_type not in allowed:
        return {"success": False, "message":"Unsupported file format", "object": None, "errors":["only pdf and docx allowed"]}
    # upload resume to cloudinary
    uploaded_url = upload_resume_file(resume.file, f"resume_{current_user.id}_{job.id}")
    app = crud.create_application(db, current_user.id, job.id, uploaded_url, cover_letter)
    # send email to company
    company = db.query(models.User).filter(models.User.id == job.created_by).first()
    html = f"<p>New application for {job.title} from {current_user.full_name}. Resume: {uploaded_url}</p>"
    send_email_background(background_tasks, company.email, f"New applicant for {job.title}", html)
    return {"success": True, "message":"Applied successfully", "object": {"application_id": str(app.id)}, "errors": None}

# track my applications (applicant)
@router.get("/me", response_model=PaginatedResponse)
def my_applications(page: int = 1, size: int = 10, company_name: str = None, job_status: str = None,
                    app_status: list[str] = Query(None), sort_by: str = "applied_at", order: str = "desc",
                    db: Session = Depends(get_db), current_user = Depends(auth_lib.require_role("applicant"))):
    q = db.query(models.Application).join(models.Job).join(models.User, models.Job.created_by == models.User.id).filter(models.Application.applicant_id == current_user.id)
    if company_name:
        q = q.filter(models.User.full_name.ilike(f"%{company_name}%"))
    if job_status:
        q = q.filter(models.Job.status == models.JobStatus(job_status))
    if app_status:
        q = q.filter(models.Application.status.in_(app_status))
    total = q.count()
    # sort
    ordering = {
        "applied_at": models.Application.applied_at,
        "company_name": models.User.full_name,
        "application_status": models.Application.status,
        "job_title": models.Job.title
    }.get(sort_by, models.Application.applied_at)
    if order.lower() == "desc":
        ordering = ordering.desc()
    else:
        ordering = ordering.asc()
    items = q.order_by(ordering).offset((page-1)*size).limit(size).all()
    out = []
    for a in items:
        out.append({
            "application_id": str(a.id),
            "job_title": a.job.title,
            "company_name": a.job.owner.full_name,
            "status": a.status.value,
            "applied_at": a.applied_at.isoformat()
        })
    return {"success": True, "message":"Applications fetched", "object": out, "pageNumber": page, "pageSize": size, "totalSize": total, "errors": None}

# company: view job applications for job
@router.get("/jobs/{job_id}", response_model=PaginatedResponse)
def view_job_applications(job_id: str, status: str = None, page: int = 1, size: int = 10,
                          db: Session = Depends(get_db), current_user = Depends(auth_lib.require_role("company"))):
    job = crud.get_job(db, job_id)
    if not job:
        return {"success": False, "message":"Job not found", "object": None, "errors": ["not found"]}
    if str(job.created_by) != str(current_user.id):
        return {"success": False, "message":"Unauthorized access", "object": None, "errors": ["unauthorized"]}
    q = db.query(models.Application).filter(models.Application.job_id == job.id)
    if status:
        q = q.filter(models.Application.status == models.ApplicationStatus(status))
    total = q.count()
    items = q.order_by(models.Application.applied_at.desc()).offset((page-1)*size).limit(size).all()
    out = []
    for a in items:
        out.append({
            "applicant_name": a.applicant.full_name,
            "resume_link": a.resume_link,
            "cover_letter": a.cover_letter,
            "status": a.status.value,
            "applied_at": a.applied_at.isoformat()
        })
    return {"success": True, "message":"Applications fetched", "object": out, "pageNumber": page, "pageSize": size, "totalSize": total, "errors": None}

# update application status (company)
@router.patch("/{application_id}/status", response_model=BaseResponse)
def update_application_status(application_id: str, payload: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user = Depends(auth_lib.require_role("company"))):
    new_status = payload.get("new_status")
    if new_status not in [s.value for s in models.ApplicationStatus]:
        return {"success": False, "message":"Invalid status", "object": None, "errors": ["invalid status"]}
    app = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not app:
        return {"success": False, "message":"Application not found", "object": None, "errors": ["not found"]}
    job = db.query(models.Job).filter(models.Job.id == app.job_id).first()
    if str(job.created_by) != str(current_user.id):
        return {"success": False, "message":"Unauthorized", "object": None, "errors": ["unauthorized"]}
    app.status = models.ApplicationStatus(new_status)
    db.add(app)
    db.commit()
    db.refresh(app)
    # email on certain statuses
    if new_status in ["Interview", "Rejected", "Hired"]:
        subj = ""
        if new_status == "Interview":
            subj = f"You've been selected for an interview for {job.title}"
            body = f"Congrats! You've been invited to interview for {job.title}. Status: {new_status}"
        elif new_status == "Rejected":
            subj = f"Application update for {job.title}"
            body = f"We regret to inform you that your application for {job.title} was {new_status}."
        else:
            subj = f"Congratulations! Hired for {job.title}"
            body = f"Great news — your application for {job.title} resulted in {new_status}!"
        send_email_background(background_tasks, app.applicant.email, subj, body)
    return {"success": True, "message":"Application updated", "object": {"application_id": str(app.id), "status": app.status.value}, "errors": None}
