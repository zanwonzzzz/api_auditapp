from fastapi import FastAPI
import aiomysql
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse
from app.v1.controllers.consultas import *

app = FastAPI()
load_dotenv()
#esta tabla va a estar guardada en cache para filtrarla en android
@app.get("/consultas")
async def end_pointOrdenesSinAuditor():
    return await OrdenesSinAuditor()

#consultas del dashboard de auditorias
#no puedo llamar directamente a una funcion debe estar dentro de otra funcion
@app.get("/total/{inicio}/{fin}/{estatus_auditoria}")
async def endpoint_graficasAuditorias(inicio, fin, estatus_auditoria):
    return await graficasAuditorias(inicio, fin, estatus_auditoria)


 