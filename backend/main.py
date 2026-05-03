from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from routers import auth, properties, clients, leads, dashboard, ai, corretores
from routers import public
from routers import imobiliarias
from database import init_db
from config import settings
from middleware import AccessControlMiddleware  # ✅ RBAC habilitado


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="Imovia API",
    description="API para gestão imobiliária com IA",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de controle de acesso (RBAC habilitado)
app.add_middleware(AccessControlMiddleware)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(properties.router, prefix="/properties", tags=["Imóveis"])
app.include_router(clients.router, prefix="/clients", tags=["Clientes"])
app.include_router(leads.router, prefix="/leads", tags=["Leads"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(ai.router, prefix="/ai", tags=["IA"])
app.include_router(corretores.router, prefix="/corretores", tags=["Corretores"])
app.include_router(imobiliarias.router, prefix="/imobiliarias", tags=["Imobiliárias"])

# Router público (Área do Cliente)
app.include_router(public.router, prefix="/public", tags=["Área do Cliente"])


@app.get("/")
async def root():
    return {"message": "Imovia API - Gestão Imobiliária com IA", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}