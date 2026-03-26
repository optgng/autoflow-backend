"""Telegram endpoints with rate limiting and atomic token linking (SEC-01, SEC-02)."""
from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.api.deps import CurrentUser, DBSession
from src.config import settings
from src.schemas.telegram import (
    GenerateLinkResponse,
    TelegramLinkRequest,
    TelegramLinkResponse,
    TelegramStatusResponse,
)
from src.services.telegram_service import TelegramService

router = APIRouter(prefix="/telegram", tags=["Telegram"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/generate-link", response_model=GenerateLinkResponse, summary="Генерация deep link для Telegram")
async def generate_link(
    current_user: CurrentUser,
    session: DBSession,
) -> GenerateLinkResponse:
    """Генерирует deep link для привязки Telegram. Действует 10 минут."""
    service = TelegramService(session)
    token = await service.generate_link_token(current_user.id)
    deep_link = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start=auth_{token.token}"
    return GenerateLinkResponse(deep_link=deep_link, token=token.token, expires_at=token.expires_at)


@router.post("/link", response_model=TelegramLinkResponse, summary="Привязка Telegram (вызывается n8n)")
@limiter.limit("5/15minutes")  # SEC-01: rate limit 5 attempts per 15 min per IP
async def link_telegram(
    request: Request,
    data: TelegramLinkRequest,
    session: DBSession,
) -> TelegramLinkResponse:
    """
    Привязывает telegram_id к аккаунту через одноразовый токен.
    Токен потребляется атомарно (UPDATE...WHERE used=FALSE).
    Одинаковый ответ при неверном и просроченном токене (не раскрывает причину).
    """
    service = TelegramService(session)
    try:
        user = await service.link_telegram(
            raw_token=data.token,
            telegram_id=data.telegram_id,
            telegram_username=data.telegram_username,
        )
        return TelegramLinkResponse(success=True, message="Аккаунт успешно привязан", username=user.username)
    except ValueError:
        # SEC-01: unified error response — do not leak reason
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )


@router.get("/status", response_model=TelegramStatusResponse, summary="Статус привязки Telegram")
async def get_status(current_user: CurrentUser, session: DBSession) -> TelegramStatusResponse:
    return TelegramStatusResponse(
        is_linked=current_user.telegram_id is not None,
        telegram_username=current_user.telegram_username,
        telegram_id=current_user.telegram_id,
    )


@router.delete("/unlink", status_code=status.HTTP_204_NO_CONTENT, summary="Отвязать Telegram")
async def unlink_telegram(current_user: CurrentUser, session: DBSession) -> None:
    if not current_user.telegram_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Telegram не привязан")
    service = TelegramService(session)
    await service.unlink_telegram(current_user.id)
