import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.schemas.users import (
    RequestEmail,
    Token,
    User,
    UserCreate,
    UserLogin,
    ResetPassword,
    UserCacheModel,
)
from src.services.auth import create_access_token, get_email_from_token, Hash
from src.services.email import send_email, send_reset_password_email
from src.services.users import UserService
from src.services.redis_cache import redis_cache


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Register a new user with email confirmation.

    This endpoint creates a new user, hashes their password, and
    sends a confirmation email with a verification link.

    Args:
        user_data (UserCreate): User registration data.
        background_tasks (BackgroundTasks): Background task manager.
        request (Request): FastAPI request object.
        db (Session): Database session dependency.

    Returns:
        User: The created user object.
    """

    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists.",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login", response_model=Token)
async def login_user(body: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.

    This endpoint verifies the user's email and password, and if
    valid, returns a JWT token.

    Args:
        body (UserLogin): User login credentials.
        db (Session): Database session dependency.

    Returns:
        Token: A JWT access token.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email is not verified.",
        )
    if not user or not Hash().verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_access_token(data={"sub": user.username})

    cached_user = UserCacheModel(
        id=user.id,
        username=user.username,
        email=user.email,
        is_verified=user.is_verified,
        role=user.role,
    ).dict()

    if redis_cache.redis:
        await redis_cache.set(f"user:{user.username}", cached_user, expire=3600)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user's email using a token.

    This endpoint extracts the email from the verification token and
    updates the user's status to `is_verified = True`.

    Args:
        token (str): Email verification token.
        db (Session): Database session dependency.

    Returns:
        dict: A message indicating the verification status.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.is_verified:
        return {"message": "Your email is already verified."}
    await user_service.confirmed_email(email)
    return {"message": "Email successfully verified."}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Resend email verification link.

    This endpoint sends a new email verification link to the user.

    Args:
        body (RequestEmail): Request containing the user's email.
        background_tasks (BackgroundTasks): Background task manager.
        request (Request): FastAPI request object.
        db (Session): Database session dependency.

    Returns:
        dict: A message indicating that the verification email was sent.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.is_verified:
        return {"message": "Your email is already verified."}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for verification instructions."}


@router.post("/forgot-password")
async def forgot_password_request(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Sends an email with a password reset link.
    """
    logging.info(f"Password reset request for {body.email}")

    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        logging.error(f"User {body.email} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not user.is_verified:
        logging.error(f"User {body.email} has not verified email")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is not verified",
        )
    try:
        reset_token = await create_access_token(data={"sub": user.email})
        logging.info(f"Password reset token generated: {reset_token}")
        background_tasks.add_task(
            send_reset_password_email,
            user.email,
            user.username,
            str(request.base_url).rstrip("/"),
            reset_token,
        )
        logging.info(f"Reset instructions email sent to {user.email}")

        return {"message": "Check your email for password reset instructions"}
    except Exception as e:
        logging.error(f"Password reset error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/reset-password/{token}")
async def reset_password(
    token: str, body: ResetPassword, db: Session = Depends(get_db)
):
    """
    Set a new password for the user.
    """
    email = await get_email_from_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    hashed_password = Hash().get_password_hash(body.new_password)
    await user_service.reset_password(user.id, hashed_password)

    return {"message": "Password successfully changed"}
