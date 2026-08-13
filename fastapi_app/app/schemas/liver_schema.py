from pydantic import BaseModel


class LiverPredictionInput(BaseModel):
    age: float
    gender: int
    tot_bilirubin: float
    direct_bilirubin: float
    tot_proteins: float
    albumin: float
    ag_ratio: float
    sgpt: float
    sgot: float
    alkphos: float