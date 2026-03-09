"""
Category repository.
"""
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.category import Category
from src.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Repository for Category model."""

    def __init__(self, session: AsyncSession):
        super().__init__(Category, session)

    async def get_user_categories(
        self,
        user_id: int,
        category_type: str | None = None,
        include_system: bool = True,
    ) -> list[Category]:
        """
        Get categories for user (including system categories).
        
        Args:
            user_id: User ID
            category_type: Filter by type (income/expense/transfer)
            include_system: Include system categories
            
        Returns:
            List of categories
        """
        query = select(Category).where(Category.is_active == True)  # noqa: E712
        
        if include_system:
            # User's own categories OR system categories
            query = query.where(
                or_(Category.user_id == user_id, Category.is_system == True)  # noqa: E712
            )
        else:
            query = query.where(Category.user_id == user_id)
        
        if category_type:
            query = query.where(Category.category_type == category_type)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_system_categories(
        self, category_type: str | None = None
    ) -> list[Category]:
        """
        Get system categories.
        
        Args:
            category_type: Filter by type
            
        Returns:
            List of system categories
        """
        query = select(Category).where(Category.is_system == True)  # noqa: E712
        
        if category_type:
            query = query.where(Category.category_type == category_type)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_name_and_type(
        self, user_id: int, name: str, category_type: str
    ) -> Category | None:
        """
        Get category by name and type.
        
        Args:
            user_id: User ID
            name: Category name
            category_type: Category type
            
        Returns:
            Category or None
        """
        result = await self.session.execute(
            select(Category)
            .where(Category.user_id == user_id)
            .where(Category.name == name)
            .where(Category.category_type == category_type)
        )
        return result.scalar_one_or_none()

    async def create_default_categories(self, user_id: int) -> list[Category]:
        """
        Create default categories for new user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of created categories
        """
        default_categories = [
            # Expense categories
            {"name": "Продукты", "category_type": "expense", "icon": "🛒"},
            {"name": "Транспорт", "category_type": "expense", "icon": "🚗"},
            {"name": "Развлечения", "category_type": "expense", "icon": "🎉"},
            {"name": "Здоровье", "category_type": "expense", "icon": "💊"},
            {"name": "Одежда", "category_type": "expense", "icon": "👕"},
            {"name": "Коммунальные", "category_type": "expense", "icon": "🏠"},
            {"name": "Образование", "category_type": "expense", "icon": "📚"},
            {"name": "Прочее", "category_type": "expense", "icon": "📦"},
            # Income categories
            {"name": "Зарплата", "category_type": "income", "icon": "💰"},
            {"name": "Фриланс", "category_type": "income", "icon": "💻"},
            {"name": "Инвестиции", "category_type": "income", "icon": "📈"},
            {"name": "Подарки", "category_type": "income", "icon": "🎁"},
            {"name": "Прочее", "category_type": "income", "icon": "💵"},
        ]
        
        created = []
        for cat_data in default_categories:
            category = await self.create(user_id=user_id, **cat_data)
            created.append(category)
        
        return created

