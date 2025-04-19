import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.database import get_db
from src.schemas.users import User
from src.services.auth import get_current_user, get_current_admin_user
from src.services.upload_file import UploadFileService
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def me(user: User = Depends(get_current_user)):
    """
    Retrieve the authenticated user's profile information.

    Args:
        user (User): The currently authenticated user.

    Returns:
    """
    try:
        logging.info(f"Profile request for user: {user.username}")
        return user
    except Exception as e:
        logging.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the user's avatar by uploading a new image.

    Args:
        file (UploadFile): The image file to upload.
        user (User): The currently authenticated user.
        db (AsyncSession): Database session dependency.

    Returns:
        User: The updated user profile with the new avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
