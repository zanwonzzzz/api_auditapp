from fastapi import FastAPI
import aiomysql
from dotenv import load_dotenv
import os
from jose import jwt
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from app.v1.model.Auditorias import *

load_dotenv()
#esto se usa para decir q pues se espera un token en los headers
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)
#consultas
#esta tabla va a estar guardada en cache para filtrarla en android y con polling estar actualizando sin volverla a cargar
async def encode_token(payload:dict)->str:
    token = jwt.encode(payload,"super-secret","HS256")
    return token
#el depends significa que pues dependemos de lo que realise tal funcion que se llama

async def decode_token(token:Annotated[str,Depends(oauth2_scheme)])->dict:
    user = jwt.decode(token,"super-secret","HS256")
    return user

async def conexion():
    conn = await aiomysql.connect(host=os.getenv('DB_HOST'), 
                                port=int(os.getenv('DB_PORT')),
                                    user=os.getenv('DB_USERNAME'), 
                                    password=os.getenv('DB_PASSWORD'),
                                        db=os.getenv('DB_DATABASE'))
    return conn        

async def authenticate_user(user,conn=""):
    cur = await conn.cursor()
    sql = "SELECT * FROM Auditores WHERE user = %s"
    await cur.execute(sql,(user))
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return {"idAuditor":r[0][0],"Nombre_Auditor":r[0][1],"user":r[0][4]}


async def login(user,conn=""):
    user = await authenticate_user(user,conn)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = await encode_token(user)
    return {"token":token,"user":user}
 
#estoi pensando en agregar notificaciones cuando se asgine una nueva auditoria 
async def OrdenesPendientes(fk_auditor_auditoria_det="",conn=""):
    cur = await conn.cursor()
    sql = "SELECT DISTINCT ad.Folio_Pisa,tic.Terminal,tic.Puerto,tic.Distrito,tic.Tecnologia,COPE,ad.Estatus_Auditoria,tic.Latitud AS Latitud,tic.Longitud AS Longitud,analisis_bd.qm_tac_prod_bolsa.Latitud AS Latitud_Bolsa,analisis_bd.qm_tac_prod_bolsa.Longitud AS Longitud_Bolsa,tic.Direccion_Cliente FROM db_apps.Auditorias_Det AS ad INNER JOIN db_apps.tecnico_instalaciones_coordiapp AS tic ON ad.Folio_Pisa = tic.Folio_Pisa INNER JOIN db_apps.Auditores AS au ON ad.FK_Auditor_Auditoria_Det = au.idAuditor INNER JOIN db_apps.copes ON FK_Cope = id LEFT JOIN analisis_bd.qm_tac_prod_bolsa ON ad.Folio_Pisa = qm_tac_prod_bolsa.Folio_Pisa AND qm_tac_prod_bolsa.ORIGEN = 'bolsa' WHERE tic.Fecha_Asignacion_Auditor >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR) AND ad.FK_Auditor_Auditoria_Det = %s AND ad.Estatus_Auditoria = 'PENDIENTE' ORDER BY tic.Fecha_Asignacion_Auditor ASC;"
    await cur.execute(sql,(fk_auditor_auditoria_det))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (
        content= {
            'Ordenes_Pendientes':r
        },
        status_code=200
    )

async def OrdenesDetalle(folio_pisa,conn=""):
    cur = await conn.cursor()
    sql = "SELECT ad.Folio_Pisa, tic.Terminal, tic.Puerto, tic.Distrito, tic.Tecnologia,  tic.Cliente_Titular, tic.Telefono_Cliente, COPE, ad.Estatus_Auditoria, tic.Latitud, tic.Longitud,tic.Direccion_Cliente,tic.Apellido_Paterno_Titular,tic.Apellido_Materno_Titular,ad.F_Terminal_Abierta_Cerrada FROM db_apps.Auditorias_Det AS ad INNER JOIN db_apps.tecnico_instalaciones_coordiapp AS tic ON ad.Folio_Pisa = tic.Folio_Pisa INNER JOIN db_apps.Auditores AS au ON ad.FK_Auditor_Auditoria_Det = au.idAuditor INNER JOIN db_apps.copes ON FK_Cope = id WHERE ad.Folio_Pisa = %s ORDER BY tic.Fecha_Asignacion_Auditor ASC;"
    await cur.execute(sql,(folio_pisa))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse ( content= { 'Detalle_Orden':r},status_code=200)

async def ValorClientePresente(folio_pisa,campos,conn=""):
    cur = await conn.cursor()
    sql =  f"SELECT {campos} FROM db_apps.Auditorias_Det WHERE Folio_Pisa = %s"
    await cur.execute(sql,(folio_pisa))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (content= {'Valor':r},status_code=200)

async def ValoresTecnico(folio_pisa,campos,conn=""):
    cur = await conn.cursor()
    sql =  f"SELECT {campos} FROM db_apps.tecnico_instalaciones_coordiapp  WHERE Folio_Pisa = %s"
    await cur.execute(sql,(folio_pisa))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (content= {'Valor_Tecnico':r},status_code=200)

#sirbe solo falta aser esto mas sencillo los campos
async def InsertNoExiste(folio_pisa, actu, conn=""):
    campos = [
        ("Foto_No_Ubicado", actu.Foto_No_Ubicado),
        ("Inicio_Traslado", actu.Inicio_Traslado),
        ("Evidencia_Instalacion", actu.Evidencia_Instalacion),
        ("P_Observaciones_Finales", actu.P_Observaciones_Finales),
        ("P_Domicilio", actu.P_Domicilio),
        ("Estatus_Auditoria", actu.Estatus_Auditoria),
        ("lat_auditor", actu.lat_auditor),
        ("lon_auditor", actu.lon_auditor),
        ("Fecha_Fin", actu.Fecha_Fin),
        ("Existe_Instalacion", actu.Existe_Instalacion),
        ("Foto_No_Ubicado",actu.Foto_No_Ubicado),
        ("Inicio_Traslado",actu.Inicio_Traslado),
        ("Fecha_Inicio" ,actu.Fecha_Inicio),
        ("Fin_Traslado ",actu.Fin_Traslado),
        ("Tecnologia_Auditor ",actu.Tecnologia_Auditor),
        ("Coincide_Instalacion ",actu.Coincide_Instalacion),
        ("P_Cliente ",actu.P_Cliente),
        ("Foto_Domicilio ",actu.Foto_Domicilio),
        ("F_Terminal_Abierta_Cerrada ",actu.F_Terminal_Abierta_Cerrada),
        ("P_Terminal_Abierta_Cerrada ",actu.P_Terminal_Abierta_Cerrada),
        ("F_Metraje ",actu.F_Metraje),
        ("P_Metraje ",actu.P_Metraje),
        ("F_Trayectoria_Tubo_Ranurado ",actu.F_Trayectoria_Tubo_Ranurado),
        ("P_Trayectoria_Tubo_Ranurado ",actu.P_Trayectoria_Tubo_Ranurado),
        ("P_Distrito ",actu.P_Distrito),
        ("P_Terminal ",actu.P_Terminal),
        ("F_SujetadorCinta ",actu.F_SujetadorCinta),
        ("P_SujetadorCinta ",actu.P_SujetadorCinta),
        ("F_SelloPas ",actu.F_SelloPas),
        ("P_SelloPas ",actu.P_SelloPas),
        ("F_Trayectoria_Remata ",actu.F_Trayectoria_Remata),
        ("P_Trayectoria_Remata ",actu.P_Trayectoria_Remata),
        ("F_Trayectoria_predios ",actu.F_Trayectoria_predios),
        ("P_Trayectoria_predios ",actu.P_Trayectoria_predios),
        ("F_Trayectoria_arbol ",actu.F_Trayectoria_arbol),
        ("P_Trayectoria_arbol ",actu.P_Trayectoria_arbol),
        ("F_Trayectoria_Estructuras ",actu.F_Trayectoria_Estructuras),
        ("P_Trayectoria_Estructuras ",actu.P_Trayectoria_Estructuras),
        ("F_Trayectoria_CableCFE ",actu.F_Trayectoria_CableCFE),
        ("P_Trayectoria_CableCFE ",actu.P_Trayectoria_CableCFE),
        ("F_Trayectoria_Electrica ",actu.F_Trayectoria_Electrica),
        ("P_Trayectoria_Electrica ",actu.P_Trayectoria_Electrica),
        ("P_MaterialUtil_OS ",actu.P_MaterialUtil_OS),
        ("P_Metraje_obtenido ",actu.P_Metraje_obtenido),
        ("P_Infraestructura ",actu.P_Infraestructura),
        ("P_Ret_Infra ",actu.P_Ret_Infra),
        ("P_Observaciones_Cliente ",actu.P_Observaciones_Cliente),
        ("P_Observaciones_Tecnicas ",actu.P_Observaciones_Tecnicas),
        ("P_Observaciones_Finales ",actu.P_Observaciones_Finales),
        ("servicio_instalado ",actu.servicio_instalado),
        ("interesa_contratar ",actu.interesa_contratar),
        ("contacto_cliente ",actu.contacto_cliente),
        ("P_Tecnico_Identificado ",actu.P_Tecnico_Identificado),
        ("P_Uniforme ",actu.P_Uniforme),
        ("P_Ubicacion_Instalacion ",actu.P_Ubicacion_Instalacion),
        ("Evalua_Instalacion ",actu.Evalua_Instalacion),
        ("Persona_recibio ",actu.Persona_recibio),
        ("Parentesco ",actu.Parentesco),
        ("P_Limpieza_Instalacion ",actu.P_Limpieza_Instalacion),
        ("P_Cobro_Instalacion ",actu.P_Cobro_Instalacion),
        ("P_Pruebas_Navegacion ",actu.P_Pruebas_Navegacion),
        ("P_NumCont_garantia ",actu.P_NumCont_garantia),
        ("Acceso_Domicilio ",actu.Acceso_Domicilio),
        ("F_Sujetador ",actu.F_Sujetador),
        ("P_Sujetador ",actu.P_Sujetador),
        ("F_Roseta ",actu.F_Roseta),
        ("P_Roseta ",actu.P_Roseta),
        ("F_Roseta_Conector ",actu.F_Roseta_Conector),
        ("P_Roseta_Conector ",actu.P_Roseta_Conector),
        ("F_DIT ",actu.F_DIT),
        ("P_DIT ",actu.P_DIT),
        ("F_CordonInt_Gris ",actu.F_CordonInt_Gris),
        ("P_CordonInt_Gris ",actu.P_CordonInt_Gris),
        ("F_Esquina ",actu.F_Esquina),
        ("P_Esquina ",actu.P_Esquina),
        ("F_ModemFuncionando ",actu.F_ModemFuncionando),
        ("P_ModemFuncionando ",actu.P_ModemFuncionando),
        ("F_UbicacionModem ",actu.F_UbicacionModem),
        ("P_UbicacionModem ",actu.P_UbicacionModem)
    ]

    campos_actualizar = [(k, v) for k, v in campos if v not in [None, ""]]


    if not campos_actualizar:
        return JSONResponse(content={'msg': 'No hay campos para actualizar'}, status_code=400)

    set_sql = ", ".join([f"{k} = %s" for k, v in campos_actualizar])
    valores = [v for k, v in campos_actualizar]
    valores.append(folio_pisa)

    sql = f"UPDATE db_apps.Auditorias_Det SET {set_sql} WHERE Folio_Pisa = %s"

    cur = await conn.cursor()
    await cur.execute(sql, tuple(valores))
    await conn.commit()
    await cur.close()
    conn.close()
    return JSONResponse(content={'msg': 'Actualizado exitosamente'}, status_code=200)

async def copes(conn=""):
    cur = await conn.cursor()
    sql = "SELECT id,COPE FROM db_apps.copes"
    await cur.execute(sql)
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (content= {'Copes':r},status_code=200)


async def DistritosPorCopes(id_cope,conn=""):
    cur = await conn.cursor()
    sql = "SELECT id_distrito, distrito FROM distritos WHERE fk_cope = %s"
    await cur.execute(sql,(id_cope))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (content= {'Distritos':r},status_code=200)


async def ValidarFolio(folio_pisa,conn=""):
    cur = await conn.cursor()
    sql = "SELECT COUNT(*) FROM db_apps.tecnico_instalaciones_coordiapp  WHERE Folio_Pisa = %s"
    await cur.execute(sql,(folio_pisa))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (content= {'Validacion_Folio':r},status_code=200)

async def InsertAuditoria(folio_pisa,actu,conn=""):
    cur = await conn.cursor()
    sql = """INSERT INTO Auditorias_Det (Folio_Pisa, FK_Auditor_Auditoria_Det, Fecha_Inicio, Estatus_Auditoria,Tecnologia_Auditor)
            VALUES (%s, %s, %s, %s,%s)"""
    await cur.execute(sql,(folio_pisa,actu.Auditor,actu.Fecha_Inicio,actu.Estatus_Auditoria,actu.Tecnologia_Auditor))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (content= {'msg':'Datos insertados correctamente'},status_code=200)
