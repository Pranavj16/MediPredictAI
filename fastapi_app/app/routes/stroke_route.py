from fastapi import APIRouter

from app.schemas.stroke_schema import StrokeInput
from app.services.stroke_service import predict_stroke

router = APIRouter(
    prefix="/predict",
    tags=["Stroke Prediction"]
)


@router.post("/stroke")
def predict(data: StrokeInput):

    return predict_stroke(data.dict())