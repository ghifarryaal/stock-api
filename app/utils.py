from __future__ import annotations

import datetime as _dt
import uuid as _uuid
from typing import Any, Dict, List, Optional

def utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).isoformat()

def new_request_id() -> str:
    return str(_uuid.uuid4())

def envelope(*, tool: str, operation: str, data: Any = None, success: bool = True,
             request_id: Optional[str] = None, errors: Optional[List[Dict[str, Any]]] = None,
             meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "tool": tool,
        "operation": operation,
        "request_id": request_id or new_request_id(),
        "success": bool(success),
        "ts_utc": utc_now_iso(),
        "data": data if data is not None else {},
        "errors": errors or [],
        "meta": meta or {},
    }
