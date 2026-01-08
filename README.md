# IDX Unified Market Intel API

Gabungan:
- Fundamental (YFinance)
- Technical (tanpa `pandas_ta` — pakai perhitungan RSI/MACD/SMA/Bollinger sendiri)
- Whale alert (rasio volume & turnover sederhana)
- News analysis (format ala "The Veteran Analyst", tanpa janji profit)

## Run (local)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Buka:
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Endpoint utama: gabungan analisis
### POST /v1/analyze/{ticker}
Contoh (gabungkan semuanya + inject news & whale dari n8n):
```json
POST http://localhost:8000/v1/analyze/BBCA.JK
{
  "style": "ringkas",
  "with_news": true,
  "with_whale": true,
  "news_items": [
    {"title":"Contoh judul", "description":"ringkas", "link":"https://..."}
  ],
  "whale": {
    "symbol":"BBCA.JK",
    "today_price": 8075,
    "today_turnover": 1234567890,
    "vol_ratio": 2.1,
    "is_whale_detected": true,
    "analysis_note": "Aktivitas volume 2.10x lebih tinggi dari rata-rata."
  }
}
```

### GET /v1/analyze/{ticker}
Cepat untuk tes:
`GET http://localhost:8000/v1/analyze/BBCA.JK?style=ringkas`

## Tools-style endpoint (buat n8n)
`POST /v1/tools/execute`

Contoh:
```json
{
  "tool": "idx_stock_analyzer",
  "operation": "analyze",
  "input": {
    "ticker": "BBCA.JK",
    "with_news": false,
    "with_whale": true
  }
}
```

## Catatan penting
- Ini **bukan** nasihat investasi dan tidak menjanjikan hasil. Output bersifat heuristik/logis untuk membantu membaca konteks.
- Untuk news: rekomendasi terbaik adalah **n8n yang fetch RSS**, lalu inject `news_items` ke endpoint analyze.
