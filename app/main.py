from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, APP_VERSION

# ===== ROUTERS =====
from app.routers.health import router as health_router
from app.routers.analyze import router as analyze_router
from app.routers.news import router as news_router
from app.routers.whale import router as whale_router
from app.routers.tools import router as tools_router

# ===== CHART =====
from app.routers.chart import router as chart_router
from app.routers.chart_fundamental import router as chart_fundamental_router
from app.routers.chart_balance import router as chart_balance_router   # ✅ BARU
from app.routers.chart_cashflow import router as chart_cashflow_router # ✅ BARU


# ===== APP =====
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # nanti bisa diketatkan di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== REGISTER ROUTERS =====
app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(news_router)
app.include_router(whale_router)
app.include_router(tools_router)

# ===== CHART ROUTERS =====
app.include_router(
    chart_router,
    prefix="/api",
    tags=["Chart"]
)

app.include_router(
    chart_fundamental_router,
    prefix="/api",
    tags=["Chart Fundamental"]
)

app.include_router(
    chart_balance_router,
    prefix="/api",
    tags=["Chart Balance Sheet"]
)

app.include_router(
    chart_cashflow_router,
    prefix="/api",
    tags=["Chart Cash Flow"]
)


# ===== ROOT =====
@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "docs": "/docs"
    }
