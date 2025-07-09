from fastapi import FastAPI,APIRouter
import aiomysql
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse
from app.v1.controllers.consultas import *
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173"
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(
    prefix="/api",
    dependencies= [Depends(oauth2_scheme)]
)

load_dotenv()
class Auditores(BaseModel):
    user:str

@app.post("/login")
async def endpoint_Login(user:Auditores,conn:str = Depends(conexion)):
    return await login(user,conn)
# guarda el token shares preferences y cuando sierre sesion pues se borra pero es desde android
@router.get("/logout")
async def endpoint_logout():
    return  JSONResponse(content={"msg":"Sesion Cerrada exitosamente"},status_code=200)
#no puedo llamar directamente a una funcion debe estar dentro de otra funcion
@router.get("/pendientes/{fk_auditor_auditoria_det}/")
async def endpoint_OrdenesPendientes(fk_auditor_auditoria_det:int,conn:str = Depends(conexion)):
    return await OrdenesPendientes(fk_auditor_auditoria_det,conn)
    
@router.get("/detalle/ordenes/{folio_pisa}/")
async def endpoint_DetalleOrdenes(folio_pisa,conn:str = Depends(conexion)):
    return await OrdenesDetalle(folio_pisa,conn)  

@router.get("/valores/{folio_pisa}/{campos}")
async def endpoint_Valores(
    folio_pisa:str,
    campos:str,
    conn:str = Depends(conexion)):
    return await ValorClientePresente(folio_pisa,campos,conn)  
#ignorar los campos q no bengan
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

@router.put("/no/existe/{folio_pisa}/")
async def endpoint_InsertNoExiste(folio_pisa,actu:Auditorias,conn:str = Depends(conexion)):
    return await InsertNoExiste(folio_pisa,actu,conn)  
#convertir todas las rutas a JEISON
@router.get("/copes")
async def endpoint_Copes(conn:str = Depends(conexion)):
    return await copes(conn)  

#las rutas de app son las que estan disponibles siempre las del apirouter se agregan
app.include_router(router)