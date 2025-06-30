from fastapi import FastAPI
import aiomysql
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse

app = FastAPI()
divisiones = []
load_dotenv()

@app.get("/consultas")
async def test_example():
    conn = await aiomysql.connect(host=os.getenv('DB_HOST'), 
                                  port=int(os.getenv('DB_PORT')),
                                       user=os.getenv('DB_USERNAME'), 
                                       password=os.getenv('DB_PASSWORD'),
                                        db=os.getenv('DB_DATABASE'))

    cur = await conn.cursor()
    await cur.execute("SELECT tic.Folio_Pisa,d.Division,ad.Nombre_Auditor,ad.Apellido_Auditor,c.COPE,a.area,tic.Distrito,tic.Tecnologia,tic.Terminal,tic.Tipo_Instalacion,tic.Metraje,tic.FK_Auditor,ads.Asigno FROM tecnico_instalaciones_coordiapp tic LEFT JOIN copes c ON FK_Cope = c.id JOIN areas a ON c.FK_Area = a.idAreas JOIN divisiones d ON a.FK_Division = d.idDivision LEFT JOIN Auditores ad ON tic.FK_Auditor = ad.idAuditor LEFT JOIN Auditorias_Det ads ON tic.Folio_Pisa = ads.Folio_Pisa WHERE tic.Estatus_Orden = 'COMPLETADA' AND (tic.FK_Auditor = 0 OR ads.Estatus_Auditoria = 'PENDIENTE') AND tic.Step_Registro = 5 ORDER BY tic.Distrito ASC")
    print(cur.description)
    r = await cur.fetchall()
    print(r)
    await cur.close()
    conn.close()



 