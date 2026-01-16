from fastapi import APIRouter, HTTPException
from app.services.chart_fundamental import get_fundamental_chart

router = APIRouter()

@router.get("/chart/fundamental/{ticker}")
async def chart_fundamental_api(ticker: str):

    data = get_fundamental_chart(ticker)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Data fundamental tidak ditemukan"
        )

    return data
