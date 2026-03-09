"""
Category service.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.repositories.category_repo import CategoryRepository
from src.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate


class CategoryService:
    """Service for category management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.category_repo = CategoryRepository(session)

    async def create_category(
        self, user_id: int, data: CategoryCreate
    ) -> CategoryResponse:
        """
        Create new category.
        
        Args:
            user_id: User ID
            data: Category data
            
        Returns:
            Created category
        """
        category = await self.category_repo.create(
            user_id=user_id,
            name=data.name,
            category_type=data.category_type,
            icon=data.icon,
            color=data.color,
            is_system=False,
            is_active=True,
        )
        
        return CategoryResponse.model_validate(category)

    async def get_user_categories(
        self,
        user_id: int,
        category_type: str | None = None,
        include_system: bool = True,
    ) -> list[CategoryResponse]:
        """
        Get categories for user.
        
        Args:
            user_id: User ID
            category_type: Filter by type
            include_system: Include system categories
            
        Returns:
            List of categories
        """
        categories = await self.category_repo.get_user_categories(
            user_id=user_id,
            category_type=category_type,
            include_system=include_system,
        )
        
        return [CategoryResponse.model_validate(cat) for cat in categories]

    async def update_category(
        self, category_id: int, user_id: int, data: CategoryUpdate
    ) -> CategoryResponse:
        """
        Update category.
        
        Args:
            category_id: Category ID
            user_id: User ID (for authorization)
            data: Update data
            
        Returns:
            Updated category
            
        Raises:
            NotFoundError: If category not found
            AuthorizationError: If user doesn't own category or it's system
        """
        category = await self.category_repo.get_by_id(category_id)
        
        if not category:
            raise NotFoundError("Category not found")
        
        if category.is_system:
            raise AuthorizationError("Cannot modify system category")
        
        if category.user_id != user_id:
            raise AuthorizationError("Access denied to this category")
        
        updated = await self.category_repo.update(
            category_id,
            **data.model_dump(exclude_unset=True),
        )
        
        return CategoryResponse.model_validate(updated)

    async def delete_category(self, category_id: int, user_id: int) -> bool:
        """
        Delete category.
        
        Args:
            category_id: Category ID
            user_id: User ID (for authorization)
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundError: If category not found
            AuthorizationError: If user doesn't own category or it's system
        """
        category = await self.category_repo.get_by_id(category_id)
        
        if not category:
            raise NotFoundError("Category not found")
        
        if category.is_system:
            raise AuthorizationError("Cannot delete system category")
        
        if category.user_id != user_id:
            raise AuthorizationError("Access denied to this category")
        
        return await self.category_repo.delete(category_id)

