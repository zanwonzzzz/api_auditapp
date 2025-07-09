from fastapi import FastAPI
import aiomysql
from dotenv import load_dotenv
import os
from jose import jwt
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)

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

async def authenticate_user(user:dict,conn=""):
    cur = await conn.cursor()
    sql = "SELECT * FROM Auditores WHERE user = %s"
    await cur.execute(sql,(user))
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    #revisar esta condicion
    if user != r[0][4]:
        return  False
    return user

async def login(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],conn=""):
    user = await authenticate_user(form_data.user,conn)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    users = {'user':user}
    return await encode_token(users) 

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
    return JSONResponse ( content= { 'Detalle de Orden':r},status_code=200)

async def ValorClientePresente(folio_pisa,campos,conn=""):
    cur = await conn.cursor()
    sql =  f"SELECT {campos} FROM db_apps.Auditorias_Det WHERE Folio_Pisa = %s"
    await cur.execute(sql,(folio_pisa))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (content= {'Valor':r},status_code=200)

#sirbe pero obio debo mandar los datos llenos pq sino se sobreescriben
#ignorart los que bienen bacios
async def InsertNoExiste(folio_pisa,actu,conn=""):
    cur = await conn.cursor()
    sql = """
    UPDATE db_apps.Auditorias_Det SET Foto_No_Ubicado= %s,Inicio_Traslado = %s,Evidencia_Instalacion = %s,P_Observaciones_Finales = %s,P_Domicilio = %s,Estatus_Auditoria = %s,lat_auditor = %s,lon_auditor = %s, 
    Fecha_Fin = %s,Existe_Instalacion = %s WHERE Folio_Pisa = %s"""
    await cur.execute(sql,(actu.Foto_No_Ubicado,actu.Inicio_Traslado,actu.Evidencia_Instalacion,actu.P_Observaciones_Finales,actu.P_Domicilio,actu.Estatus_Auditoria,actu.lat_auditor,actu.lon_auditor,actu.Fecha_Fin,actu.Existe_Instalacion,folio_pisa))
    print(cur.description)
    #para guardar cambios
    await conn.commit()
    await cur.close()
    conn.close()
    return JSONResponse (content= {'msg':'Insertado Exitosamente'},status_code=200)

async def copes(conn=""):
    cur = await conn.cursor()
    await cur.execute(sql = "SELECT id,COPE FROM db_apps.copes")
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
    return JSONResponse (content= {'Distritos por Cope':r},status_code=200)


async def ValidarFolio(folio_pisa,conn=""):
    cur = await conn.cursor()
    sql = "SELECT COUNT(*) FROM db_apps.tecnico_instalaciones_coordiapp  WHERE Folio_Pisa = %s"
    await cur.execute(sql,(folio_pisa))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (content= {'Validacion del Folio':r},status_code=200)
