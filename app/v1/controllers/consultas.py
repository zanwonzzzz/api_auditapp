from fastapi import FastAPI
import aiomysql
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse
from pydantic import BaseModel
load_dotenv()
#consultas
#esta tabla va a estar guardada en cache para filtrarla en android y con polling estar actualizando sin volverla a cargar

async def conexion():
    conn = await aiomysql.connect(host=os.getenv('DB_HOST'), 
                                port=int(os.getenv('DB_PORT')),
                                    user=os.getenv('DB_USERNAME'), 
                                    password=os.getenv('DB_PASSWORD'),
                                        db=os.getenv('DB_DATABASE'))
    return conn                              
async def OrdenesSinAuditor():
    conn = await conexion()
    cur = await conn.cursor()
    await cur.execute("SELECT tic.Folio_Pisa,d.Division,ad.Nombre_Auditor,ad.Apellido_Auditor,c.COPE,a.area,tic.Distrito,tic.Tecnologia,tic.Terminal,tic.Tipo_Instalacion,tic.Metraje,tic.FK_Auditor,ads.Asigno FROM tecnico_instalaciones_coordiapp tic LEFT JOIN copes c ON FK_Cope = c.id JOIN areas a ON c.FK_Area = a.idAreas JOIN divisiones d ON a.FK_Division = d.idDivision LEFT JOIN Auditores ad ON tic.FK_Auditor = ad.idAuditor LEFT JOIN Auditorias_Det ads ON tic.Folio_Pisa = ads.Folio_Pisa WHERE tic.Estatus_Orden = 'COMPLETADA' AND (tic.FK_Auditor = 0 OR ads.Estatus_Auditoria = 'PENDIENTE') AND tic.Step_Registro = 5 ORDER BY tic.Distrito ASC")
    print(cur.description)
    r = await cur.fetchall()
    print(r)
    await cur.close()
    conn.close()

#consultas del dashboard de auditorias
async def graficasAuditorias(inicio,fin,estatus_auditoria):
        conn = await conexion()
        cur = await conn.cursor()
        if estatus_auditoria == 'PENDIENTE':
            sql = "SELECT COUNT(DISTINCT Folio_Pisa) as total_auditorias FROM Auditorias_Det WHERE `Estatus_Auditoria` != %s AND `Fecha_Inicio` >= %s AND `Fecha_Inicio` < %s"
        else:   
             sql = "SELECT COUNT(DISTINCT Folio_Pisa) as total_auditorias FROM Auditorias_Det WHERE `Estatus_Auditoria` = %s AND `Fecha_Inicio` >= %s AND `Fecha_Inicio` < %s" 
        await cur.execute(sql,(inicio,fin,estatus_auditoria))
        print(cur.description)
        r = await cur.fetchall()
        await cur.close()
        conn.close()
        return JSONResponse (
            content= {
                'total_auditorias':r
            },
            status_code=200
        )
#estoi pensando en agregar notificaciones cuando se asgine una nueva auditoria 
async def OrdenesPendientes(fk_auditor_auditoria_det=""):
    conn = await conexion()
    cur = await conn.cursor()
    sql = "SELECT DISTINCT ad.Folio_Pisa,tic.Terminal,tic.Puerto,tic.Distrito,tic.Tecnologia,COPE,ad.Estatus_Auditoria,tic.Latitud AS Latitud,tic.Longitud AS Longitud,analisis_bd.qm_tac_prod_bolsa.Latitud AS Latitud_Bolsa,analisis_bd.qm_tac_prod_bolsa.Longitud AS Longitud_Bolsa,tic.Direccion_Cliente FROM db_apps.Auditorias_Det AS ad INNER JOIN db_apps.tecnico_instalaciones_coordiapp AS tic ON ad.Folio_Pisa = tic.Folio_Pisa INNER JOIN db_apps.Auditores AS au ON ad.FK_Auditor_Auditoria_Det = au.idAuditor INNER JOIN db_apps.copes ON FK_Cope = id LEFT JOIN analisis_bd.qm_tac_prod_bolsa ON ad.Folio_Pisa = qm_tac_prod_bolsa.Folio_Pisa AND qm_tac_prod_bolsa.ORIGEN = 'bolsa' WHERE tic.Fecha_Asignacion_Auditor >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR) AND ad.FK_Auditor_Auditoria_Det = %s AND ad.Estatus_Auditoria = 'PENDIENTE' ORDER BY tic.Fecha_Asignacion_Auditor ASC;"
    await cur.execute(sql,(fk_auditor_auditoria_det))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (
        content= {
            'Ordenes Pendientes':r
        },
        status_code=200
    )

async def OrdenesDetalle(folio_pisa):
    conn = await conexion()
    cur = await conn.cursor()
    sql = "SELECT ad.Folio_Pisa, tic.Terminal, tic.Puerto, tic.Distrito, tic.Tecnologia,  tic.Cliente_Titular, tic.Telefono_Cliente, COPE, ad.Estatus_Auditoria, tic.Latitud, tic.Longitud,tic.Direccion_Cliente,tic.Apellido_Paterno_Titular,tic.Apellido_Materno_Titular,ad.F_Terminal_Abierta_Cerrada FROM db_apps.Auditorias_Det AS ad INNER JOIN db_apps.tecnico_instalaciones_coordiapp AS tic ON ad.Folio_Pisa = tic.Folio_Pisa INNER JOIN db_apps.Auditores AS au ON ad.FK_Auditor_Auditoria_Det = au.idAuditor INNER JOIN db_apps.copes ON FK_Cope = id WHERE ad.Folio_Pisa = %s ORDER BY tic.Fecha_Asignacion_Auditor ASC;"
    await cur.execute(sql,(folio_pisa))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (
        content= {
            'Detalle de Orden':r
        },
        status_code=200
    )

async def ValorClientePresente(folio_pisa,campos):
    conn = await conexion()
    cur = await conn.cursor()
    sql =  f"SELECT {campos} FROM db_apps.Auditorias_Det WHERE Folio_Pisa = %s"
    await cur.execute(sql,(folio_pisa))
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (
        content= {
            'Valor':r
        },
        status_code=200
    )



#sirbe pero obio debo mandar los datos llenos pq sino se sobreescriben
async def InsertNoExiste(folio_pisa,actu):
    conn = await conexion()
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
    return JSONResponse (
        content= {
           'msg':'Insertado Exitosamente'
        },
        status_code=200
    )

async def copes():

    conn = await conexion()
    cur = await conn.cursor()
    await cur.execute(sql = "SELECT id,COPE FROM db_apps.copes")
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (
        content= {
            'Copes':r
        },
        status_code=200
    )


async def DistritosPorCopes(id_cope):

    conn = await conexion()
    cur = await conn.cursor()
   await cur.execute(sql = "SELECT id_distrito, distrito FROM distritos WHERE fk_cope = %s")
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (
        content= {
            'Distritos por Cope':r
        },
        status_code=200
    )


async def ValidarFolio(folio_pisa):

    conn = await conexion()
    cur = await conn.cursor()
    await cur.execute(sql = "SELECT COUNT(*) FROM db_apps.tecnico_instalaciones_coordiapp  WHERE Folio_Pisa = %s")
    print(cur.description)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return JSONResponse (
        content= {
            'Validacion del Folio':r
        },
        status_code=200
    )
