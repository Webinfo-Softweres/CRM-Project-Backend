from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.api import api_router
from db.session import engine
from models import Base

app = FastAPI(
    title="CRM Workflow Management API",
    version="1.0.0",
    redirect_slashes=True
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "CRM Workflow Management API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
