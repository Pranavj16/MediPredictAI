from pydantic import BaseModel


class KidneyPredictionInput(BaseModel):
    age: float
    bp: float
    sg: float
    al: float
    su: float
    rbc: str
    pc: str
    pcc: str
    ba: str
    bgr: float
    bu: float
    sc: float
    sod: float
    pot: float
    hemo: float
    pcv: float
    wc: float
    rc: float
    htn: str
    dm: str
    cad: str
    appet: str
    pe: str
    ane: str