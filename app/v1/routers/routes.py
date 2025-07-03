from fastapi import FastAPI
import aiomysql
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse
from app.v1.controllers.consultas import *
from pydantic import BaseModel

app = FastAPI()
load_dotenv()
#esta tabla va a estar guardada en cache para filtrarla en android
@app.get("/ordenes/sin")
async def end_pointOrdenesSinAuditor():
    return await OrdenesSinAuditor()

class Auditores(BaseModel):
    user:str

@app.post("/login")
async def endpoint_Login(user:Auditores):
    return await Login(user)

#consultas del dashboard de auditorias
#no puedo llamar directamente a una funcion debe estar dentro de otra funcion
@app.get("/pendientes/{fk_auditor_auditoria_det}/")
async def endpoint_OrdenesPendientes(fk_auditor_auditoria_det):
    return await OrdenesPendientes(fk_auditor_auditoria_det)
    
@app.get("/detalle/ordenes/{folio_pisa}/")
async def endpoint_DetalleOrdenes(folio_pisa):
    return await OrdenesDetalle(folio_pisa)  

@app.get("/valores/{folio_pisa}/{campos}")
async def endpoint_Valores(folio_pisa,campos):
    return await ValorClientePresente(folio_pisa,campos)  

class Auditorias(BaseModel):
    Evidencia_Instalacion:str | None = None
    P_Observaciones_Finales:str | None = None
    P_Domicilio:str | None = None
    Estatus_Auditoria:str | None = None
    lat_auditor:str | None = None
    lon_auditor:str | None = None
    Fecha_Fin:str | None = None
    Existe_Instalacion:str | None = None
    Foto_No_Ubicado:str | None = None
    Inicio_Traslado :str | None = None

@app.put("/no/existe/{folio_pisa}/")
async def endpoint_InsertNoExiste(folio_pisa,actu:Auditorias):
    return await InsertNoExiste(folio_pisa,actu)  


 