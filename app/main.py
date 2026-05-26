from fastapi import FastAPI,Request
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



@app.api_route(
    "/biometric",
    methods=["GET", "POST"]
)
async def biometric_listener(request: Request):

    print("\n========= BIOMETRIC REQUEST =========\n")

    print("Method:", request.method)

    print("Headers:", request.headers)

    body = await request.body()

    print("Body:", body)

    print("\n=====================================\n")

    return {
        "status": "success"
    }


@app.on_event("startup")
async def startup_event():
    pass


@app.get("/")
def root():
    return {"message": "CRM Workflow Management API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}



#ci cd testing
