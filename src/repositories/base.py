"""
Base repository with common CRUD operations.
"""
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with CRUD operations."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Initialize repository.
        
        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session

    async def create(self, **kwargs: Any) -> ModelType:
        """
        Create new record.
        
        Args:
            **kwargs: Model fields
            
        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> ModelType | None:
        """
        Get record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> list[ModelType]:
        """
        Get all records with optional filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Filter conditions
            
        Returns:
            List of model instances
        """
        query = select(self.model)
        
        # Apply filters
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self, **filters: Any) -> int:
        """
        Count records with optional filters.
        
        Args:
            **filters: Filter conditions
            
        Returns:
            Number of records
        """
        from sqlalchemy import func
        
        query = select(func.count(self.model.id))
        
        # Apply filters
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(query)
        return result.scalar_one()

    async def update(self, id: int, **kwargs: Any) -> ModelType | None:
        """
        Update record by ID.
        
        Args:
            id: Record ID
            **kwargs: Fields to update
            
        Returns:
            Updated model instance or None
        """
        # Remove None values
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(id)
        
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .returning(self.model)
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.scalar_one_or_none()

    async def delete(self, id: int) -> bool:
        """
        Delete record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def exists(self, **filters: Any) -> bool:
        """
        Check if record exists.
        
        Args:
            **filters: Filter conditions
            
        Returns:
            True if exists, False otherwise
        """
        from sqlalchemy import exists as sa_exists
        
        query = select(sa_exists().where(self.model.id > 0))
        
        # Apply filters
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(query)
        return result.scalar_one()

