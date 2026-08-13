from fastapi import APIRouter

from app.schemas.heart_schema import HeartPredictionInput
from app.services.heart_service import predict_heart

router = APIRouter()


@router.post("/predict/heart")
def heart_prediction(data: HeartPredictionInput):

    result = predict_heart(data.model_dump())

    return result