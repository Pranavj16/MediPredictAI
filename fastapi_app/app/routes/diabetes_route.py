from fastapi import APIRouter

from app.schemas.diabetes_schema import DiabetesRequest
from app.services.diabetes_service import predict_diabetes

router = APIRouter()


@router.post("/predict/diabetes")
def diabetes_prediction(request: DiabetesRequest):

    result = predict_diabetes(request.model_dump())

    return result