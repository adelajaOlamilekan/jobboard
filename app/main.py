from fastapi import FastAPI
from .db import Base, engine
from .routers import auth, jobs, applications

# create tables at startup (for dev only; use alembic in prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Board API")

app.include_router(auth.router)
app.include_router(jobs.router)
# app.include_router(applications.router)
