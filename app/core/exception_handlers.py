from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import ApiException


def api_exception_handler(request: Request, exc: ApiException):
    return JSONResponse(status_code=exc.status_code, content={"code": exc.code, "message": exc.message})
