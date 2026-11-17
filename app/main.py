
from fastapi import FastAPI
from app.api.routes.documents import router as documents_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.tasks import router as tasks_router
from app.core.logging_config import setup_logging

setup_logging()
app = FastAPI(
    title="AI Work Intelligence Platform",
    description="AI-powered document and task intelligence API",
    version="1.0.0",
)
app.include_router(jobs_router)
app.include_router(tasks_router)
app.include_router(documents_router)
@app.get("/")
def root():
    return {
        "message": "AI Work Intelligence API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

