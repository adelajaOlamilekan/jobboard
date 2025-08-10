from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ..db import get_db
from .. import schemas, crud, auth as auth_lib, models
from app.auth import get_current_user
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# create job (company only)
@router.post("/", response_model=schemas.BaseResponse)
def create_job(payload: schemas.JobCreate, current_user=Depends(auth_lib.require_role("company")), db: Session = Depends(get_db)):
    job = crud.create_job(db, current_user, payload.title, payload.description, payload.location, payload.status)
    response_data = {"success": True, "message":"Job created", "object": {"id": str(job.id)}, "errors": None}
    return JSONResponse(content= response_data, status_code=status.HTTP_201_CREATED)

# update job
@router.put("/{job_id}", response_model=schemas.BaseResponse)
def update_job(job_id: str, payload: schemas.JobUpdate, current_user=Depends(auth_lib.require_role("company")), db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        return {"success": False, "message":"Job not found", "object": None, "errors": ["not found"]}
    if str(job.created_by) != str(current_user.id):
        return {"success": False, "message":"Unauthorized access", "object": None, "errors": ["unauthorized"]}
    # status transition enforcement
    if payload.status:
        allowed = {
            models.JobStatus.Draft: [models.JobStatus.Open],
            models.JobStatus.Open: [models.JobStatus.Closed],
            models.JobStatus.Closed: []
        }
        current_status = job.status
        new_status = models.JobStatus(payload.status)
        if new_status == current_status:
            pass
        else:
            if new_status not in allowed[current_status]:
                return {"success": False, "message":"Invalid status transition", "object": None, "errors": ["invalid status transition"]}
    updates = {k:v for k,v in payload.dict().items() if v is not None}
    job = crud.update_job(db, job, **updates)
    return {"success": True, "message": "Job updated", "object": {"id": str(job.id)}, "errors": None}

@router.delete("/{job_id}", response_model=schemas.BaseResponse)
def delete_job(job_id: str, current_user=Depends(auth_lib.require_role("company")), db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        return {"success": False, "message":"Job not found", "object": None, "errors": ["not found"]}
    if str(job.created_by) != str(current_user.id):
        return {"success": False, "message":"Unauthorized access", "object": None, "errors": ["unauthorized"]}
    crud.delete_job(db, job)
    return {"success": True, "message":"Job deleted", "object": None, "errors": None}

# browse jobs - accessible to all authenticated users
@router.get("/", response_model=schemas.PaginatedResponse)
def browse_jobs(q_title: Optional[str] = Query(None), q_location: Optional[str] = Query(None), company_name: Optional[str] = Query(None),
                page: int = 1, size: int = 10, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    query = db.query(models.Job).join(models.User, models.Job.created_by == models.User.id)
    if q_title:
        query = query.filter(models.Job.title.ilike(f"%{q_title}%"))
    if q_location:
        query = query.filter(models.Job.location.ilike(f"%{q_location}%"))
    if company_name:
        query = query.filter(models.User.full_name.ilike(f"%{company_name}%"))
    total = query.count()
    items = query.order_by(models.Job.created_at.desc()).offset((page-1)*size).limit(size).all()
    out = []
    for j in items:
        out.append({
            "id": str(j.id),
            "title": j.title,
            "description": j.description,
            "location": j.location,
            "status": j.status.value,
            "created_by": str(j.created_by),
            "created_at": j.created_at.isoformat()
        })
    return {"success": True, "message":"Jobs fetched", "object": out, "pageNumber": page, "pageSize": size, "totalSize": total, "errors": None}

# view job detail
@router.get("/{job_id}", response_model=schemas.BaseResponse)
def job_detail(job_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    job = crud.get_job(db, job_id)
    if not job:
        return {"success": False, "message":"Job not found", "object": None, "errors": ["not found"]}
    return {"success": True, "message":"Job fetched", "object": {
        "id": str(job.id),
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "status": job.status.value,
        "created_by": str(job.created_by),
        "created_at": job.created_at.isoformat()
    }, "errors": None}
