from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from proyectobackend.routers.clientes import router as clientes_router
from proyectobackend.routers.vehiculos import router as vehiculos_router
from proyectobackend.routers.reparaciones import router as reparaciones_router
from proyectobackend.routers.orden_trabajo_routers import (
    router as orden_trabajo_router,
)
from proyectobackend.schemas.error import ErrorDetail, ErrorResponse


app = FastAPI(
    title="API Taller Mecánico",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    respuesta = ErrorResponse(
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message="Los datos de la solicitud no son válidos",
            details=jsonable_encoder(exc.errors()),
        )
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=respuesta.model_dump(),
    )


app.include_router(clientes_router)
app.include_router(vehiculos_router)
app.include_router(reparaciones_router)
app.include_router(orden_trabajo_router)


@app.get("/")
def root():
    return {"mensaje": "API Taller Mecánico funcionando"}