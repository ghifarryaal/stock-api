from fastapi import APIRouter, HTTPException
from app.services.chart_balance import get_balance_chart

router = APIRouter()

@router.get("/chart/balance/{ticker}")
async def balance_api(ticker: str):

    data = get_balance_chart(ticker)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Data neraca tidak ditemukan"
        )

    return data
