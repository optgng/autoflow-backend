"""
Telegram endpoints.
"""
from fastapi import APIRouter, HTTPException, status

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


@router.post(
    "/generate-link",
    response_model=GenerateLinkResponse,
    summary="Генерация deep link для привязки Telegram",
)
async def generate_link(
    current_user: CurrentUser,
    session: DBSession,
) -> GenerateLinkResponse:
    """
    Генерирует одноразовый токен и deep link для привязки Telegram бота.
    Токен действителен 10 минут.
    Требует авторизации.
    """
    service = TelegramService(session)
    token   = await service.generate_link_token(current_user.id)

    deep_link = (
        f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}"
        f"?start=auth_{token.token}"
    )

    return GenerateLinkResponse(
        deep_link  = deep_link,
        token      = token.token,
        expires_at = token.expires_at,
    )


@router.post(
    "/link",
    response_model=TelegramLinkResponse,
    summary="Привязка Telegram (вызывается n8n ботом)",
)
async def link_telegram(
    data: TelegramLinkRequest,
    session: DBSession,
) -> TelegramLinkResponse:
    """
    Привязывает telegram_id к пользователю по одноразовому токену.
    Вызывается n8n workflow после команды /start auth_TOKEN.
    Авторизация пользователя НЕ требуется — только валидный токен.
    """
    service = TelegramService(session)
    try:
        user = await service.link_telegram(
            raw_token          = data.token,
            telegram_id        = data.telegram_id,
            telegram_username  = data.telegram_username,
        )
        return TelegramLinkResponse(
            success  = True,
            message  = f"Аккаунт успешно привязан",
            username = user.username,
        )
    except ValueError as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = str(e),
        )


@router.get(
    "/status",
    response_model=TelegramStatusResponse,
    summary="Статус привязки Telegram",
)
async def get_status(
    current_user: CurrentUser,
    session: DBSession,
) -> TelegramStatusResponse:
    """
    Возвращает статус привязки Telegram для текущего пользователя.
    Требует авторизации.
    """
    return TelegramStatusResponse(
        is_linked          = current_user.telegram_id is not None,
        telegram_username  = current_user.telegram_username,
        telegram_id        = current_user.telegram_id,
    )


@router.delete(
    "/unlink",
    status_code = status.HTTP_204_NO_CONTENT,
    summary     = "Отвязать Telegram",
)
async def unlink_telegram(
    current_user: CurrentUser,
    session: DBSession,
) -> None:
    """
    Отвязывает Telegram от аккаунта пользователя.
    Требует авторизации.
    """
    if not current_user.telegram_id:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = "Telegram не привязан",
        )
    service = TelegramService(session)
    await service.unlink_telegram(current_user.id)

