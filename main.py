from fastapi import FastAPI

from app.api.auth import auth_router
from app.api.user import user_router
from app.core.exception_handlers import api_exception_handler
from app.core.exceptions import ApiException
from app.core.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version='0.0.1',
    debug=settings.DEBUG,
    docs_url=f"/{settings.PROJECT_URL_PREFIX}_docs",
    redoc_url=f"/{settings.PROJECT_URL_PREFIX}_redoc",
    openapi_url=f"/{settings.PROJECT_URL_PREFIX}_openapi.json",
)

app.include_router(auth_router)
app.include_router(user_router)
app.add_exception_handler(ApiException, api_exception_handler)

# for local run with ide debugger
if __name__ == '__main__':
    from uvicorn import run

    run(app=app, host=settings.SERVICE_HOST, port=int(settings.SERVICE_PORT), log_level='info')
