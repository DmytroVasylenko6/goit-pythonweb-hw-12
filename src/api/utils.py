from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint to verify database connectivity.

    This endpoint performs a simple SQL query (`SELECT 1`) to ensure that the
    database connection is active and properly configured.

    Args:
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A success message indicating the API is running properly.

    Raises:
        HTTPException: If the database connection fails.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )

        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(f"DB error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
