from fastapi import APIRouter

from app.schemas.kidney_schema import KidneyPredictionInput
from app.services.kidney_service import predict_kidney

router = APIRouter()


@router.post("/predict/kidney")
def kidney_prediction(data: KidneyPredictionInput):

    result = predict_kidney(data.model_dump())

    return result