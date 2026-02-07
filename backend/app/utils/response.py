from typing import Any, Optional
from fastapi.responses import JSONResponse

def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> JSONResponse:
    """Standard success response"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data
        }
    )

def error_response(
    message: str = "An error occurred",
    errors: Optional[Any] = None,
    status_code: int = 400
) -> JSONResponse:
    """Standard error response"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "errors": errors
        }
    )

def paginated_response(
    data: list,
    page: int,
    limit: int,
    total: int,
    message: str = "Success"
) -> JSONResponse:
    """Paginated response"""
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": message,
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    )
