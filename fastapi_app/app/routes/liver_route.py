from fastapi import APIRouter

from app.schemas.liver_schema import LiverPredictionInput
from app.services.liver_service import predict_liver

router = APIRouter()


@router.post("/predict/liver")
def liver_prediction(data: LiverPredictionInput):

    return predict_liver(data.model_dump())