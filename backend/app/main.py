from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routes import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="API de gestion et de suivi préventif des transformateurs JIRAMA.",
    debug=settings.DEBUG,
)

# CORS limité aux origines du frontend déclarées dans .env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix="/api")