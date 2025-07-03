from pydantic import BaseModel

class Auditorias(BaseModel):
    Evidencia_Instalacion:str
    P_Observaciones_Finales:str
    P_Domicilio:str
    Estatus_Auditoria:str
    lat_auditor:str
    lon_auditor:str
    Fecha_Fin:str
    Existe_Instalacion:str

class Auditores(BaseModel):
    user:str