from fastapi import APIRouter, HTTPException
from app.services.chart import get_chart_data

router = APIRouter()

@router.get("/chart/{ticker}")
async def chart_api(ticker: str):

    data = get_chart_data(ticker)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Saham tidak ditemukan"
        )

    return data
