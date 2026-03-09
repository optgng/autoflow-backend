"""
Category endpoints.
"""
from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser, DBSession
from src.core.exceptions import AuthorizationError, NotFoundError
from src.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from src.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    current_user: CurrentUser,
    session: DBSession,
) -> CategoryResponse:
    """
    Create new category.
    
    Requires authentication.
    """
    service = CategoryService(session)
    return await service.create_category(current_user.id, data)


@router.get("", response_model=list[CategoryResponse])
async def get_categories(
    current_user: CurrentUser,
    session: DBSession,
    category_type: str | None = None,
    include_system: bool = True,
) -> list[CategoryResponse]:
    """
    Get categories for current user.
    
    Includes system categories by default.
    Requires authentication.
    """
    service = CategoryService(session)
    return await service.get_user_categories(
        current_user.id,
        category_type=category_type,
        include_system=include_system,
    )


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_user: CurrentUser,
    session: DBSession,
) -> CategoryResponse:
    """
    Update category.
    
    Cannot update system categories.
    Requires authentication and ownership.
    """
    try:
        service = CategoryService(session)
        return await service.update_category(category_id, current_user.id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> None:
    """
    Delete category.
    
    Cannot delete system categories.
    Requires authentication and ownership.
    """
    try:
        service = CategoryService(session)
        await service.delete_category(category_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

