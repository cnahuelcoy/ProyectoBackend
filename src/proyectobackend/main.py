from fastapi import FastAPI

from proyectobackend.routers.clientes import router as clientes_router
from proyectobackend.routers.vehiculos import router as vehiculos_router
from proyectobackend.routers.reparaciones import router as reparaciones_router
from proyectobackend.routers.orden_trabajo_routers import router as orden_trabajo_router

app = FastAPI(
    title="API Taller Mecánico",
    version="1.0.0",
)

app.include_router(clientes_router)
app.include_router(vehiculos_router)
app.include_router(reparaciones_router)
app.include_router(orden_trabajo_router)

@app.get("/")
def root():
    return {"mensaje": "API Taller Mecánico funcionando"}