"""
User endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy import select

from src.api.deps import CurrentUser, DBSession
from src.models.user import User
from src.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


class UserUpdate(BaseModel):
    username:  Optional[str]      = None
    email:     Optional[EmailStr] = None
    full_name: Optional[str]      = None


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    data: UserUpdate,
    current_user: CurrentUser,
    session: DBSession,
) -> UserResponse:
    """
    Update current user profile.

    Requires authentication.
    """
    if data.username and data.username != current_user.username:
        result = await session.execute(
            select(User).where(User.username == data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким username уже существует",
            )

    if data.email and data.email != current_user.email:
        result = await session.execute(
            select(User).where(User.email == data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует",
            )

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user

