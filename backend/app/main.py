from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .auth.router import router as auth_router
from .upload.router import router as upload_router
from .analytics.router import router as analytics_router
from .reporting.router import router as reporting_router

app = FastAPI(title="Smart E-Commerce Analytics API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(analytics_router)
app.include_router(reporting_router)
