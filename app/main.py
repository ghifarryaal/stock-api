from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, APP_VERSION
from app.routers.health import router as health_router
from app.routers.analyze import router as analyze_router
from app.routers.news import router as news_router
from app.routers.whale import router as whale_router
from app.routers.tools import router as tools_router

# 🔥 TAMBAHAN
from app.routers.chart import router as chart_router


app = FastAPI(title=APP_NAME, version=APP_VERSION)

# relaxed CORS for local dev / n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== EXISTING ROUTERS =====
app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(news_router)
app.include_router(whale_router)
app.include_router(tools_router)

# ===== NEW CHART ROUTER =====
app.include_router(
    chart_router,
    prefix="/api",
    tags=["Chart"]
)

@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "docs": "/docs"
    }
