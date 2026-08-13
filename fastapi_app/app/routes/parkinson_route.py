from fastapi import APIRouter

from app.schemas.parkinson_schema import ParkinsonInput
from app.services.parkinson_service import predict_parkinson


router = APIRouter(
    prefix="/predict",
    tags=["Parkinson Disease"]
)


@router.post("/parkinson")
def predict(data: ParkinsonInput):

    return predict_parkinson(data.dict())