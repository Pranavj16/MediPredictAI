from fastapi import FastAPI

from app.routes.diabetes_route import router as diabetes_router
from app.routes.heart_route import router as heart_router
from app.routes.kidney_route import router as kidney_router
from app.routes.liver_route import router as liver_router
from app.routes.parkinson_route import router as parkinson_router
from app.routes.stroke_route import router as stroke_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MediPredict AI API",
    version="1.0.0"
)

# Enable CORS for production readiness
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diabetes_router)
app.include_router(heart_router)
app.include_router(kidney_router)
app.include_router(liver_router)
app.include_router(parkinson_router)
app.include_router(stroke_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to MediPredict AI API"
    }