from fastapi import APIRouter, HTTPException
from app.services.chart_cashflow import get_cashflow_chart

router = APIRouter()

@router.get("/chart/cashflow/{ticker}")
async def cashflow_api(ticker: str):

    data = get_cashflow_chart(ticker)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Data arus kas tidak ditemukan"
        )

    return data
