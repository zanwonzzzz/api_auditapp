from pydantic import BaseModel

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
    Fecha_Inicio :str | None = None
    Fin_Traslado :str | None = None
    Tecnologia_Auditor :str | None = None
    Coincide_Instalacion :str | None = None
    P_Cliente :str | None = None
    Foto_Domicilio :str | None = None
    F_Terminal_Abierta_Cerrada :str | None = None
    P_Terminal_Abierta_Cerrada :str | None = None
    F_Metraje :str | None = None
    P_Metraje :str | None = None
    F_Trayectoria_Tubo_Ranurado :str | None = None
    P_Trayectoria_Tubo_Ranurado :str | None = None
    P_Distrito :str | None = None
    P_Terminal :str | None = None
    F_SujetadorCinta :str | None = None
    P_SujetadorCinta :str | None = None
    F_SelloPas :str | None = None
    P_SelloPas :str | None = None
    F_Trayectoria_Remata :str | None = None
    P_Trayectoria_Remata :str | None = None
    F_Trayectoria_predios :str | None = None
    P_Trayectoria_predios :str | None = None
    F_Trayectoria_arbol :str | None = None
    P_Trayectoria_arbol :str | None = None
    F_Trayectoria_Estructuras :str | None = None
    P_Trayectoria_Estructuras :str | None = None
    F_Trayectoria_CableCFE :str | None = None
    P_Trayectoria_CableCFE :str | None = None
    F_Trayectoria_Electrica :str | None = None
    P_Trayectoria_Electrica :str | None = None
    P_MaterialUtil_OS :str | None = None
    P_Metraje_obtenido :str | None = None
    P_Infraestructura :str | None = None
    P_Ret_Infra :str | None = None
    P_Observaciones_Cliente :str | None = None
    P_Observaciones_Tecnicas :str | None = None
    P_Observaciones_Finales :str | None = None
    servicio_instalado :str | None = None
    interesa_contratar :str | None = None
    contacto_cliente :str | None = None
    P_Tecnico_Identificado :str | None = None
    P_Uniforme :str | None = None
    P_Ubicacion_Instalacion :str | None = None
    Evalua_Instalacion :str | None = None
    Persona_recibio :str | None = None
    Parentesco :str | None = None
    P_Limpieza_Instalacion :str | None = None
    P_Cobro_Instalacion :str | None = None
    P_Pruebas_Navegacion :str | None = None
    P_NumCont_garantia :str | None = None
    Acceso_Domicilio :str | None = None
    F_Sujetador :str | None = None
    P_Sujetador :str | None = None
    F_Roseta :str | None = None
    P_Roseta :str | None = None
    F_Roseta_Conector :str | None = None
    P_Roseta_Conector :str | None = None
    F_DIT :str | None = None
    P_DIT :str | None = None
    F_CordonInt_Gris :str | None = None
    P_CordonInt_Gris :str | None = None
    F_Esquina :str | None = None
    P_Esquina :str | None = None
    F_ModemFuncionando :str | None = None
    P_ModemFuncionando :str | None = None
    F_UbicacionModem :str | None = None
    P_UbicacionModem :str | None = None


class Login_data(BaseModel):
    user:str

class AuditoriaNueva(BaseModel):
    Auditor:int
    Fecha_Inicio:str
    Estatus_Auditoria:str
    Tecnologia_Auditor:str | None = None
