# Структура и исходный код проекта
Сгенерировано: Thu Mar 26 09:01:51 PM UTC 2026

<document path="./main.py">
```py
"""
FastAPI application entry point.
Запуск: python main.py
"""
import sys
from pathlib import Path

# Добавляем src/ в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from src.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

```
</document>

<document path="./README.md">
```md
# autoflow-backend```
</document>

<document path="./alembic.ini">
```ini
# A generic, single database configuration.

[alembic]
script_location = alembic
timezone = UTC

# Можно оставить пустым — будем брать URL из кода
sqlalchemy.url =

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python>=3.9 or backports.zoneinfo library.
# Any required deps can installed by adding `alembic[tz]` to the pip requirements
# string value is passed to ZoneInfo()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to alembic/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
# The path separator used here should be the separator specified by "version_path_separator" below.
# version_locations = %(here)s/bar:%(here)s/bat:alembic/versions

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses os.pathsep.
# If this key is omitted entirely, it falls back to the legacy behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os  # Use os.pathsep. Default configuration used for new projects.

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```
</document>

<document path="./scripts/create_tables.py">
```py
"""
Create all database tables.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import init_db
from src.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


async def main():
    """Create all tables."""
    logger.info("Creating database tables...")
    
    try:
        await init_db()
        logger.info("✅ All tables created successfully!")
    except Exception as e:
        logger.error("❌ Failed to create tables", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(main())

```
</document>

<document path="./scripts/test_api.py">
```py
"""
Quick API test script.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

BASE_URL = "http://localhost:8080/api/v1"


async def main():
    """Run API tests."""
    async with httpx.AsyncClient() as client:
        print("🧪 Starting API tests...\n")
        
        # 1. Register user
        print("1️⃣ Registering user...")
        register_response = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "testuser@example.com",
                "username": "testuser",
                "password": "TestPassword123",
                "full_name": "Test User",
            },
        )
        
        if register_response.status_code == 201:
            print("✅ User registered successfully")
            data = register_response.json()
            access_token = data["tokens"]["access_token"]
            print(f"   Access token: {access_token[:50]}...")
        elif register_response.status_code == 409:
            print("⚠️  User already exists, trying to login...")
            
            # Login instead
            login_response = await client.post(
                f"{BASE_URL}/auth/login",
                json={
                    "email": "testuser@example.com",
                    "password": "TestPassword123",
                },
            )
            
            if login_response.status_code == 200:
                print("✅ Logged in successfully")
                data = login_response.json()
                access_token = data["tokens"]["access_token"]
            else:
                print(f"❌ Login failed: {login_response.text}")
                return
        else:
            print(f"❌ Registration failed: {register_response.text}")
            return
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Get current user
        print("\n2️⃣ Getting current user info...")
        me_response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
        if me_response.status_code == 200:
            user = me_response.json()
            print(f"✅ User: {user['username']} ({user['email']})")
        else:
            print(f"❌ Failed: {me_response.text}")
        
        # 3. Create account
        print("\n3️⃣ Creating account...")
        account_response = await client.post(
            f"{BASE_URL}/accounts",
            headers=headers,
            json={
                "name": "Тестовая карта",
                "account_type": "card",
                "currency": "RUB",
                "balance": "50000.00",
                "bank_name": "Тестовый банк",
            },
        )
        
        if account_response.status_code == 201:
            account = account_response.json()
            account_id = account["id"]
            print(f"✅ Account created: {account['name']} (ID: {account_id})")
            print(f"   Balance: {account['balance']} {account['currency']}")
        else:
            print(f"❌ Failed: {account_response.text}")
            return
        
        # 4. Get categories
        print("\n4️⃣ Getting categories...")
        categories_response = await client.get(
            f"{BASE_URL}/categories", headers=headers
        )
        
        if categories_response.status_code == 200:
            categories = categories_response.json()
            print(f"✅ Found {len(categories)} categories")
            expense_categories = [c for c in categories if c["category_type"] == "expense"]
            if expense_categories:
                category_id = expense_categories[0]["id"]
                print(f"   Using category: {expense_categories[0]['name']} (ID: {category_id})")
        else:
            print(f"❌ Failed: {categories_response.text}")
            return
        
        # 5. Create transaction
        print("\n5️⃣ Creating expense transaction...")
        transaction_response = await client.post(
            f"{BASE_URL}/transactions",
            headers=headers,
            json={
                "account_id": account_id,
                "category_id": category_id,
                "transaction_date": "2026-03-10",
                "amount": "1500.00",
                "transaction_type": "expense",
                "description": "Тестовая покупка",
            },
        )
        
        if transaction_response.status_code == 201:
            transaction = transaction_response.json()
            transaction_id = transaction["id"]
            print(f"✅ Transaction created: {transaction['description']}")
            print(f"   Amount: {transaction['amount']} (ID: {transaction_id})")
        else:
            print(f"❌ Failed: {transaction_response.text}")
            return
        
        # 6. Check updated balance
        print("\n6️⃣ Checking updated account balance...")
        account_check = await client.get(
            f"{BASE_URL}/accounts/{account_id}", headers=headers
        )
        
        if account_check.status_code == 200:
            updated_account = account_check.json()
            print(f"✅ Updated balance: {updated_account['balance']} {updated_account['currency']}")
            print(f"   Expected: 48500.00 (50000 - 1500)")
        else:
            print(f"❌ Failed: {account_check.text}")
        
        # 7. Get dashboard
        print("\n7️⃣ Getting dashboard data...")
        dashboard_response = await client.get(
            f"{BASE_URL}/dashboard", headers=headers
        )
        
        if dashboard_response.status_code == 200:
            dashboard = dashboard_response.json()
            print(f"✅ Dashboard loaded")
            print(f"   Total balance: {dashboard['balance']['total_balance']}")
            print(f"   Total expense: {dashboard['income_expense']['total_expense']}")
            print(f"   Recent transactions: {len(dashboard['recent_transactions'])}")
        else:
            print(f"❌ Failed: {dashboard_response.text}")
        
        # 8. Get all transactions
        print("\n8️⃣ Getting all transactions...")
        transactions_response = await client.get(
            f"{BASE_URL}/transactions?page=1&page_size=10", headers=headers
        )
        
        if transactions_response.status_code == 200:
            transactions_data = transactions_response.json()
            print(f"✅ Found {transactions_data['total']} transactions")
            print(f"   Page: {transactions_data['page']}/{transactions_data['total_pages']}")
        else:
            print(f"❌ Failed: {transactions_response.text}")
        
        print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())

```
</document>

<document path="./src/models/contact_profile.py">
```py
"""ContactProfile — privacy-safe contact tracking via HMAC hashes."""
from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Date, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class ContactProfile(Base, TimestampMixin):
    __tablename__ = "contact_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    contact_ref: Mapped[str] = mapped_column(String(24), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(30), default="unknown", nullable=False)
    typical_amount_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    typical_amount_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    avg_frequency_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_seen_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    tx_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_label: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "Аренда", "Мама" — NO full name

    __table_args__ = (
        UniqueConstraint("telegram_id", "contact_ref", name="uq_contact_per_user"),
        {"schema": "finances"},
    )
```
</document>

<document path="./src/models/user_rule.py">
```py
"""User-defined enrichment rules."""
from sqlalchemy import BigInteger, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class UserEnrichmentRule(Base, TimestampMixin):
    __tablename__ = "user_enrichment_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # merchant_keyword|contact_ref|amount_range|combined
    match_pattern: Mapped[str] = mapped_column(String(200), nullable=False)
    action_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    __table_args__ = {"schema": "finances"}
```
</document>

<document path="./src/models/user.py">
```py
"""
User model.
"""
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, String, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.account import Account


class User(Base, TimestampMixin):
    """User model."""
    
    __tablename__ = "users"
    __table_args__ = {"schema": "finances"}
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, unique=True, index=True
    )

    telegram_username: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    # Relationships
    accounts: Mapped[List["Account"]] = relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    telegram_link_tokens: Mapped[list["TelegramLinkToken"]] = relationship(
        "TelegramLinkToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

```
</document>

<document path="./src/models/base.py">
```py
"""
Base model with common fields.
"""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:  # если ты не задаёшь __tablename__ явно
        return cls.__name__.lower()

    __table_args__ = {"schema": "finances"}

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

```
</document>

<document path="./src/models/telegram_link_token.py">
```py
"""
Telegram link token model.
"""
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class TelegramLinkToken(Base):
    __tablename__ = "telegram_link_tokens"
    __table_args__ = {"schema": "finances"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("finances.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    used: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="telegram_link_tokens")

```
</document>

<document path="./src/models/budget.py">
```py
"""
Budget model for expense tracking.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin
from src.models.category import Category
from src.models.user import User


class Budget(Base, TimestampMixin):
    """Budget model for expense limits."""
    
    __tablename__ = "budgets"
    __table_args__ = {"schema": "finances"}
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("finances.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("finances.categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="NULL for total budget",
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    period_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="daily, weekly, monthly, yearly",
    )
    
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    category: Mapped["Category"] = relationship("Category")
    
    def __repr__(self) -> str:
        return f"<Budget(id={self.id}, name={self.name}, amount={self.amount})>"

```
</document>

<document path="./src/models/category.py">
```py
"""
Category model for transactions.
"""
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.transaction import Transaction
    from src.models.user import User


class Category(Base, TimestampMixin):
    """Transaction category model."""
    
    __tablename__ = "categories"
    __table_args__ = {"schema": "finances"}
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("finances.users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="NULL for system categories",
    )
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="income, expense, transfer",
    )
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="System category (cannot be deleted by user)",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="category",
    )
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name}, type={self.category_type})>"

```
</document>

<document path="./src/models/account.py">
```py
"""
Account database model.
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DECIMAL,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.transaction import Transaction
    from src.models.user import User

class Account(Base):
    """Account model for storing user accounts (cards, wallets, etc)."""

    __tablename__ = "accounts"
    __table_args__ = {"schema": "finances"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("finances.users.id", ondelete="CASCADE"), nullable=False
    )

    # Account details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    balance: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2), nullable=False, default=Decimal("0.00")
    )

    # Optional fields
    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    account_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_four_digits: Mapped[str | None] = mapped_column(String(4), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    include_in_total: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships - ИСПРАВЛЕНО: добавлен foreign_keys
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="account",
        foreign_keys="Transaction.account_id",  # ← ИСПРАВЛЕНИЕ
        cascade="all, delete-orphan",
    )

    user: Mapped["User"] = relationship("User", back_populates="accounts")

    # Constraints
    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_balance_positive"),
        CheckConstraint(
            "account_type IN ('card', 'bank_account', 'cash', 'investment', 'crypto', 'other')",
            name="check_account_type",
        ),
        Index("idx_accounts_user", "user_id"),
        Index("idx_accounts_type", "account_type"),
        {"schema": "finances"}
    )

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, name={self.name}, balance={self.balance})>"

```
</document>

<document path="./src/models/transaction.py">
```py
"""Transaction model with enrichment fields (Block 3)."""
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean, CheckConstraint, Date, DateTime, ForeignKey,
    Index, Integer, Numeric, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.account import Account
    from src.models.category import Category


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "finances"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("finances.users.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("finances.accounts.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("finances.categories.id", ondelete="SET NULL"), nullable=True)
    target_account_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("finances.accounts.id", ondelete="SET NULL"), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
    import_source: Mapped[str] = mapped_column(String(20), nullable=False, server_default="manual")

    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    receipt_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Enrichment fields (added in migration 002_enrichment) ──────────────────
    enriched_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    enriched_subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    enriched_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    income_type: Mapped[str | None] = mapped_column(String(50), nullable=True)   # operational|oneoff|return|internal
    expense_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # regular|subscription|oneoff|investment|debt_payment
    exclude_from_metrics: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_group_payment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    net_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    linked_tx_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("finances.transactions.id"), nullable=True)
    enrichment_source: Mapped[str | None] = mapped_column(String(20), nullable=True)   # rule|llm|user
    enrichment_confidence: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    review_status: Mapped[str] = mapped_column(String(20), default="auto", nullable=False)  # auto|pending|confirmed|rejected
    user_rule_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    enriched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    contact_ref: Mapped[str | None] = mapped_column(String(24), nullable=True, index=True)

    # ── Relationships ───────────────────────────────────────────────────────────
    account: Mapped["Account"] = relationship("Account", back_populates="transactions", foreign_keys=[account_id])
    category: Mapped["Category | None"] = relationship("Category", back_populates="transactions")
    target_account: Mapped["Account | None"] = relationship("Account", foreign_keys=[target_account_id])

    __table_args__ = (
        CheckConstraint("transaction_type IN ('income', 'expense', 'transfer')", name="check_transaction_type"),
        CheckConstraint("amount > 0", name="check_amount_positive"),
        Index("idx_transactions_user_date", "user_id", "transaction_date"),
        Index("idx_transactions_account", "account_id"),
        Index("idx_transactions_category", "category_id"),
        Index("idx_transactions_type", "transaction_type"),
        Index("idx_transactions_review_status", "review_status"),
        Index("idx_transactions_contact_ref", "contact_ref"),
        {"schema": "finances"},
    )
```
</document>

<document path="./src/models/habit_log.py">
```py
from sqlalchemy import ForeignKey, Date, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from src.models.base import Base

class HabitLog(Base):
    __tablename__ = "habit_logs"
    # Кортеж для комбинации Constraints и аргументов таблицы
    __table_args__ = (
        UniqueConstraint('habit_id', 'date', name='uq_habit_date'),
        {"schema": "finances"}
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Ссылка на таблицу habits внутри схемы finances
    habit_id: Mapped[int] = mapped_column(ForeignKey("finances.habits.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True)

    habit: Mapped["Habit"] = relationship("Habit", back_populates="logs")
```
</document>

<document path="./src/models/__init__.py">
```py
"""
Database models.
"""
from src.models.base import Base

# Базовые модели сначала (без зависимостей)
from src.models.user import User
from src.models.account import Account
from src.models.category import Category  # убедитесь, что есть и импортируется

# Dependent модели после
from src.models.budget import Budget
from src.models.transaction import Transaction

from src.models.habit import Habit
from src.models.habit_log import HabitLog

__all__ = [
    "Base",
    "User",
    "Account",
    "Category",
    "Transaction",
    "Budget",
    "Habit",
    "HabitLog",
]

```
</document>

<document path="./src/models/habit.py">
```py
from sqlalchemy import ForeignKey, String, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from src.models.base import Base, TimestampMixin

class HabitFrequency(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"

class Habit(Base, TimestampMixin):
    __tablename__ = "habits"
    __table_args__ = {"schema": "finances"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("finances.users.id", ondelete="CASCADE"), nullable=False)
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    color: Mapped[str] = mapped_column(String, default="#3b82f6")
    icon: Mapped[str] = mapped_column(String, default="target")
    frequency: Mapped[HabitFrequency] = mapped_column(Enum(HabitFrequency), default=HabitFrequency.daily)
    
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    logs: Mapped[list["HabitLog"]] = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")
```
</document>

<document path="./src/api/v1/enrichment.py">
```py
"""Enrichment review queue and confirm endpoints (Block 3)."""
from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, DBSession
from src.models.transaction import Transaction

router = APIRouter(prefix="/enrichment", tags=["Enrichment"])


class ReviewItem(BaseModel):
    transaction_id: int
    date: str
    amount: float
    tx_type: str
    contact_ref: str | None
    llm_suggestion: str | None
    llm_confidence: float | None
    review_reason: str | None
    quick_actions: list[dict]


class ReviewQueue(BaseModel):
    items: list[ReviewItem]
    total: int


class ConfirmRequest(BaseModel):
    relation_type: str
    user_label: str | None = None
    save_rule: bool = False


QUICK_ACTIONS = [
    {"label": "Обязательный платёж", "value": "obligatory"},
    {"label": "Взаиморасчёт", "value": "mutual"},
    {"label": "Долг (дал)", "value": "debt_given"},
    {"label": "Прочее", "value": "other"},
]


@router.get("/review", response_model=ReviewQueue)
async def get_review_queue(
    current_user: CurrentUser,
    session: DBSession,
    page: int = Query(1, ge=1),
    pagesize: int = Query(20, ge=1, le=100),
) -> ReviewQueue:
    """Транзакции, ожидающие подтверждения категории пользователем."""
    from src.models.account import Account
    query = (
        select(Transaction)
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == current_user.id)
        .where(Transaction.review_status == "pending")
        .order_by(Transaction.transaction_date.desc())
        .offset((page - 1) * pagesize)
        .limit(pagesize)
    )
    count_query = (
        select(func.count(Transaction.id))
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == current_user.id)
        .where(Transaction.review_status == "pending")
    )
    result = await session.execute(query)
    count_result = await session.execute(count_query)
    txs = result.scalars().all()
    total = count_result.scalar_one()

    items = [
        ReviewItem(
            transaction_id=tx.id,
            date=str(tx.transaction_date),
            amount=float(tx.amount),
            tx_type=tx.transaction_type,
            contact_ref=tx.contact_ref,
            llm_suggestion=tx.enriched_category,
            llm_confidence=float(tx.enrichment_confidence) if tx.enrichment_confidence else None,
            review_reason=None,  # stored separately in future
            quick_actions=QUICK_ACTIONS,
        )
        for tx in txs
    ]
    return ReviewQueue(items=items, total=total)


@router.post("/review/{transaction_id}/confirm", status_code=status.HTTP_200_OK)
async def confirm_review(
    transaction_id: int,
    data: ConfirmRequest,
    current_user: CurrentUser,
    session: DBSession,
) -> dict:
    """Пользователь подтверждает/уточняет категорию транзакции."""
    from src.models.account import Account
    # Ownership check
    tx_result = await session.execute(
        select(Transaction)
        .join(Account, Transaction.account_id == Account.id)
        .where(Transaction.id == transaction_id)
        .where(Account.user_id == current_user.id)
    )
    tx = tx_result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    await session.execute(
        update(Transaction)
        .where(Transaction.id == transaction_id)
        .values(
            review_status="confirmed",
            enrichment_source="user",
        )
    )

    # Update ContactProfile if contact_ref present
    if tx.contact_ref and data.user_label:
        from src.models.contact_profile import ContactProfile
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        stmt = pg_insert(ContactProfile).values(
            telegram_id=current_user.telegram_id or 0,
            contact_ref=tx.contact_ref,
            relation_type=data.relation_type,
            user_label=data.user_label,
            tx_count=1,
        ).on_conflict_do_update(
            constraint="uq_contact_per_user",
            set_={
                "relation_type": data.relation_type,
                "user_label": data.user_label,
            },
        )
        await session.execute(stmt)

    await session.commit()
    return {"status": "confirmed", "transaction_id": transaction_id}
```
</document>

<document path="./src/api/v1/dashboard.py">
```py
"""
Transaction endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DBSession
from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.schemas.base import PaginatedResponse, PaginationParams
from src.schemas.transaction import (
    TransactionCreate,
    TransactionDetail,
    TransactionFilters,
    TransactionResponse,
    TransactionUpdate,
)
from src.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    current_user: CurrentUser,
    session: DBSession,
) -> TransactionResponse:
    """
    Create new transaction.
    
    Automatically updates account balance.
    Requires authentication.
    """
    try:
        service = TransactionService(session)
        return await service.create_transaction(current_user.id, data)
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("", response_model=PaginatedResponse)
async def get_transactions(
    current_user: CurrentUser,
    session: DBSession,
    # Filters
    account_id: int | None = Query(None),
    category_id: int | None = Query(None),
    transaction_type: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    min_amount: float | None = Query(None),
    max_amount: float | None = Query(None),
    merchant: str | None = Query(None),
    search: str | None = Query(None),
    # Pagination
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    """
    Get transactions with filters and pagination.
    
    Requires authentication.
    """
    from datetime import date as date_type
    from decimal import Decimal
    
    # Parse dates
    date_from_parsed = date_type.fromisoformat(date_from) if date_from else None
    date_to_parsed = date_type.fromisoformat(date_to) if date_to else None
    
    filters = TransactionFilters(
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        date_from=date_from_parsed,
        date_to=date_to_parsed,
        min_amount=Decimal(str(min_amount)) if min_amount else None,
        max_amount=Decimal(str(max_amount)) if max_amount else None,
        merchant=merchant,
        search=search,
    )
    
    pagination = PaginationParams(page=page, page_size=page_size)
    
    service = TransactionService(session)
    return await service.get_user_transactions(current_user.id, filters, pagination)


@router.get("/{transaction_id}", response_model=TransactionDetail)
async def get_transaction(
    transaction_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> TransactionDetail:
    """
    Get transaction by ID with details.
    
    Requires authentication and ownership.
    """
    try:
        service = TransactionService(session)
        return await service.get_transaction(transaction_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    current_user: CurrentUser,
    session: DBSession,
) -> TransactionResponse:
    """
    Update transaction.
    
    Automatically adjusts account balances.
    Requires authentication and ownership.
    """
    try:
        service = TransactionService(session)
        return await service.update_transaction(transaction_id, current_user.id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> None:
    """
    Delete transaction.
    
    Automatically reverts account balance changes.
    Requires authentication and ownership.
    """
    try:
        service = TransactionService(session)
        await service.delete_transaction(transaction_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

```
</document>

<document path="./src/api/v1/telegram.py">
```py
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
```
</document>

<document path="./src/api/v1/habits.py">
```py
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import date, timedelta

from src.api.deps import CurrentUser, DBSession
from src.schemas.habit import HabitCreate, HabitUpdate, HabitResponse
from src.repositories.habit_repo import HabitRepository
from src.repositories.habit_log_repo import HabitLogRepository
from src.models.habit_log import HabitLog

router = APIRouter(prefix="/habits", tags=["Habits"])

@router.get("/", response_model=List[HabitResponse])
async def get_habits(current_user: CurrentUser, session: DBSession):
    habit_repo = HabitRepository(session)
    start_date = date.today() - timedelta(days=14)
    return await habit_repo.get_user_habits_with_logs(current_user.id, start_date)

@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(habit_in: HabitCreate, current_user: CurrentUser, session: DBSession):
    habit_repo = HabitRepository(session)
    habit = await habit_repo.create(**habit_in.model_dump(), user_id=current_user.id)
    
    habit.logs = []
    
    return habit

@router.post("/{habit_id}/toggle")
async def toggle_habit(habit_id: int, current_user: CurrentUser, session: DBSession, target_date: date = date.today()):
    habit_repo = HabitRepository(session)
    log_repo = HabitLogRepository(session)
    
    habit = await habit_repo.get_by_id(id=habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
        
    log = await log_repo.get_by_habit_and_date(habit_id, target_date)
    
    if log:
        # Меняем статус
        log.is_completed = not log.is_completed
        
        # Обновляем счетчик
        if log.is_completed:
            habit.current_streak += 1
        else:
            habit.current_streak = max(0, habit.current_streak - 1)
            
        await session.commit()
        return {"status": "updated", "is_completed": log.is_completed}
    else:
        # Создаем лог и увеличиваем стрик
        new_log = HabitLog(habit_id=habit_id, date=target_date, is_completed=True)
        habit.current_streak += 1
        
        session.add(new_log)
        await session.commit()
        return {"status": "created", "is_completed": True}

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(habit_id: int, current_user: CurrentUser, session: DBSession):
    habit_repo = HabitRepository(session)
    habit = await habit_repo.get_by_id(id=habit_id)
    
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
        
    await habit_repo.delete(id=habit_id)
    return None
```
</document>

<document path="./src/api/v1/metrics.py">
```py
"""True Finance Metrics — enrichment-aware income/expense (Block 3)."""
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, DBSession
from src.models.transaction import Transaction

router = APIRouter(prefix="/metrics", tags=["Metrics"])


class PeriodSchema(BaseModel):
    from_: str
    to: str

    class Config:
        populate_by_name = True
        fields = {"from_": "from"}


class CategoryBreakdown(BaseModel):
    category: str
    amount: float


class MetricsBreakdown(BaseModel):
    income_by_type: dict[str, float]
    expenses_by_category: list[CategoryBreakdown]


class TrueMetricsResponse(BaseModel):
    period: dict
    true_income: float
    true_expenses: float
    to_assets: float
    obligatory_transfers: float
    true_savings: float
    savings_rate: float
    pending_review_count: int
    pending_review_amount: float
    breakdown: MetricsBreakdown


@router.get("/true", response_model=TrueMetricsResponse)
async def get_true_metrics(
    current_user: CurrentUser,
    session: DBSession,
    date_from: str = Query(...),
    date_to: str = Query(...),
) -> TrueMetricsResponse:
    """
    True income/expense metrics excluding internal transfers and
    enrichment-flagged transactions.
    """
    from src.models.account import Account

    uid = current_user.id
    d_from = date.fromisoformat(date_from)
    d_to = date.fromisoformat(date_to)

    def base_query(tx_type: str):
        return (
            select(func.coalesce(func.sum(Transaction.amount), 0))
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == uid)
            .where(Transaction.transaction_type == tx_type)
            .where(Transaction.exclude_from_metrics == False)  # noqa: E712
            .where(Transaction.transaction_date >= d_from)
            .where(Transaction.transaction_date <= d_to)
        )

    # True Income: operational income only
    true_income_result = await session.execute(
        base_query("income").where(Transaction.income_type == "operational")
    )
    true_income = Decimal(str(true_income_result.scalar_one() or 0))

    # True Expenses: regular + subscription + oneoff
    true_expense_result = await session.execute(
        base_query("expense")
        .where(Transaction.expense_type.in_(["regular", "subscription", "oneoff"]))
        .with_only_columns(func.coalesce(func.sum(func.coalesce(Transaction.net_amount, Transaction.amount)), 0))
    )
    true_expenses = Decimal(str(true_expense_result.scalar_one() or 0))

    # To Assets: KARTA-VKLAD transfers
    assets_result = await session.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == uid)
        .where(Transaction.enriched_category == "Внутренний перевод")
        .where(Transaction.transaction_type == "expense")
        .where(Transaction.transaction_date >= d_from)
        .where(Transaction.transaction_date <= d_to)
    )
    to_assets = Decimal(str(assets_result.scalar_one() or 0))

    # Obligatory transfers
    obligatory_result = await session.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == uid)
        .where(Transaction.enriched_category == "Обязательные платежи")
        .where(Transaction.transaction_date >= d_from)
        .where(Transaction.transaction_date <= d_to)
    )
    obligatory_transfers = Decimal(str(obligatory_result.scalar_one() or 0))

    # Pending review
    pending_result = await session.execute(
        select(func.count(Transaction.id), func.coalesce(func.sum(Transaction.amount), 0))
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == uid)
        .where(Transaction.review_status == "pending")
        .where(Transaction.transaction_date >= d_from)
        .where(Transaction.transaction_date <= d_to)
    )
    pending_row = pending_result.one()
    pending_count = int(pending_row[0])
    pending_amount = Decimal(str(pending_row[1] or 0))

    # Expense breakdown by category
    exp_breakdown_result = await session.execute(
        select(Transaction.enriched_category, func.sum(Transaction.amount))
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == uid)
        .where(Transaction.transaction_type == "expense")
        .where(Transaction.exclude_from_metrics == False)  # noqa: E712
        .where(Transaction.transaction_date >= d_from)
        .where(Transaction.transaction_date <= d_to)
        .where(Transaction.enriched_category.isnot(None))
        .group_by(Transaction.enriched_category)
        .order_by(func.sum(Transaction.amount).desc())
    )
    exp_breakdown = [
        CategoryBreakdown(category=row[0], amount=float(row[1]))
        for row in exp_breakdown_result.all()
    ]

    true_savings = true_income - true_expenses
    savings_rate = round(float(true_savings / true_income * 100), 1) if true_income > 0 else 0.0

    return TrueMetricsResponse(
        period={"from": date_from, "to": date_to},
        true_income=float(true_income),
        true_expenses=float(true_expenses),
        to_assets=float(to_assets),
        obligatory_transfers=float(obligatory_transfers),
        true_savings=float(true_savings),
        savings_rate=savings_rate,
        pending_review_count=pending_count,
        pending_review_amount=float(pending_amount),
        breakdown=MetricsBreakdown(
            income_by_type={"operational": float(true_income)},
            expenses_by_category=exp_breakdown,
        ),
    )
```
</document>

<document path="./src/api/v1/import_api.py">
```py
"""Import endpoint with file validation (SEC-06)."""
from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter(prefix="/import", tags=["Import"])

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME = {"application/pdf"}


def _validate_pdf(content: bytes) -> None:
    """SEC-06: Basic PDF header + no embedded JS check."""
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File does not appear to be a valid PDF",
        )
    if b"/JS" in content or b"/JavaScript" in content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF contains potentially dangerous content",
        )


@router.post("/pdf")
async def import_pdf(file: UploadFile = File(...)) -> dict:
    """Import Sberbank PDF statement."""
    # SEC-06: MIME type check
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are accepted",
        )

    content = await file.read()

    # SEC-06: Size check
    if len(content) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="PDF file exceeds 10 MB limit",
        )

    _validate_pdf(content)

    # TODO: hand off to import_service as background task
    return {"status": "accepted", "size_bytes": len(content)}
```
</document>

<document path="./src/api/v1/users.py">
```py
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

```
</document>

<document path="./src/api/v1/router.py">
```py
"""
Main API v1 router.
"""
from fastapi import APIRouter

from src.api.v1 import accounts, auth, categories, dashboard, transactions, users, telegram, habits

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(accounts.router)
api_router.include_router(categories.router)
api_router.include_router(transactions.router)
api_router.include_router(dashboard.router)
api_router.include_router(users.router)
api_router.include_router(telegram.router)
api_router.include_router(habits.router)
```
</document>

<document path="./src/api/v1/categories.py">
```py
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

```
</document>

<document path="./src/api/v1/auth.py">
```py
"""Auth endpoints with rate limiting (SEC-02)."""
from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.api.deps import CurrentUser, DBSession
from src.core.exceptions import AuthenticationError, ConflictError
from src.schemas.auth import AuthResponse, LoginRequest, PasswordChangeRequest, RefreshTokenRequest, RegisterRequest, Token
from src.schemas.user import UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/hour")  # SEC-02: 3 registrations per hour per IP
async def register(request: Request, data: RegisterRequest, session: DBSession) -> AuthResponse:
    try:
        auth_service = AuthService(session)
        return await auth_service.register(data)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")  # SEC-02: 10 attempts per minute per IP
async def login(request: Request, data: LoginRequest, session: DBSession) -> AuthResponse:
    """Авторизация по email/username + пароль."""
    try:
        service = AuthService(session)
        return await service.login(data)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
@limiter.limit("30/minute")  # SEC-02
async def refresh_token(request: Request, data: RefreshTokenRequest, session: DBSession) -> Token:
    try:
        auth_service = AuthService(session)
        return await auth_service.refresh_token(data.refresh_token)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: PasswordChangeRequest, current_user: CurrentUser, session: DBSession
) -> None:
    try:
        auth_service = AuthService(session)
        await auth_service.change_password(
            user_id=current_user.id,
            old_password=data.old_password,
            new_password=data.new_password,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```
</document>

<document path="./src/api/v1/accounts.py">
```py
"""
Account endpoints.
"""
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser, DBSession
from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from src.services.account_service import AccountService
from decimal import Decimal
from typing import Dict
from sqlalchemy import func, select
from src.models.account import Account

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    current_user: CurrentUser,
    session: DBSession,
) -> AccountResponse:
    """
    Create new account.
    Только наличные (cash). Валидация типа — в схеме AccountCreate.
    """
    try:
        service = AccountService(session)
        return await service.create_account(current_user.id, data)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[AccountResponse])
async def get_accounts(
    current_user: CurrentUser,
    session: DBSession,
    include_inactive: bool = False,
) -> list[AccountResponse]:
    """Get all accounts for current user."""
    service = AccountService(session)
    return await service.get_user_accounts(current_user.id, include_inactive)


@router.get("/total-balance")
async def get_total_balance(
    current_user: CurrentUser,
    session: DBSession,
    currency: str = "RUB",
):
    """Get total balance for current user."""
    service = AccountService(session)
    total = await service.get_total_balance(current_user.id, currency)

    if total is None:
        total = Decimal("0.00")

    return {"total_balance": total, "currency": currency}


@router.get("/by-type/{account_type}", response_model=list[AccountResponse])
async def get_accounts_by_type(
    account_type: str,
    current_user: CurrentUser,
    session: DBSession,
) -> list[AccountResponse]:
    """Get accounts by type."""
    service = AccountService(session)
    return await service.get_accounts_by_type(current_user.id, account_type)

@router.get("/balances-by-currency")
async def get_balances_by_currency(
    current_user: CurrentUser,
    session: DBSession,
) -> Dict:
    """
    Суммарный баланс по каждой валюте отдельно.
    USD-наличные не суммируются с RUB — фронт отображает их раздельно.
    """
    result = await session.execute(
        select(Account.currency, func.sum(Account.balance))
        .where(Account.user_id == current_user.id)
        .where(Account.is_active == True)        # noqa: E712
        .where(Account.include_in_total == True)  # noqa: E712
        .group_by(Account.currency)
    )
    balances = {row[0]: str(row[1] or Decimal("0.00")) for row in result.all()}
    return {"balances": balances}


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> AccountResponse:
    """Get account by ID."""
    try:
        service = AccountService(session)
        return await service.get_account(account_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    data: AccountUpdate,
    current_user: CurrentUser,
    session: DBSession,
) -> AccountResponse:
    """Update account."""
    try:
        service = AccountService(session)
        return await service.update_account(account_id, current_user.id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,   detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,   detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> None:
    """Delete account (soft delete for card/bank_account, hard for cash)."""
    try:
        service = AccountService(session)
        await service.delete_account(account_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
```
</document>

<document path="./src/api/v1/transactions.py">
```py
"""Transaction endpoints — pagesize capped at 100 (SEC-03)."""
from fastapi import APIRouter, HTTPException, Query, status
from src.api.deps import CurrentUser, DBSession
from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.schemas.base import PaginatedResponse, PaginationParams
from src.schemas.transaction import TransactionCreate, TransactionDetail, TransactionFilters, TransactionResponse, TransactionUpdate
from src.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(data: TransactionCreate, current_user: CurrentUser, session: DBSession) -> TransactionResponse:
    try:
        service = TransactionService(session)
        return await service.create_transaction(current_user.id, data)
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("", response_model=PaginatedResponse)
async def get_transactions(
    current_user: CurrentUser,
    session: DBSession,
    account_id: int | None = Query(None),
    category_id: int | None = Query(None),
    transaction_type: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    min_amount: float | None = Query(None),
    max_amount: float | None = Query(None),
    merchant: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    pagesize: int = Query(20, ge=1, le=100),  # SEC-03: max 100
) -> PaginatedResponse:
    from datetime import date as datetype
    from decimal import Decimal
    date_from_parsed = datetype.fromisoformat(date_from) if date_from else None
    date_to_parsed = datetype.fromisoformat(date_to) if date_to else None
    filters = TransactionFilters(
        account_id=account_id, category_id=category_id, transaction_type=transaction_type,
        date_from=date_from_parsed, date_to=date_to_parsed,
        min_amount=Decimal(str(min_amount)) if min_amount else None,
        max_amount=Decimal(str(max_amount)) if max_amount else None,
        merchant=merchant, search=search,
    )
    pagination = PaginationParams(page=page, pagesize=pagesize)
    service = TransactionService(session)
    return await service.get_user_transactions(current_user.id, filters, pagination)


@router.get("/export")
async def export_transactions(
    current_user: CurrentUser,
    session: DBSession,
    export: bool = Query(False),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
) -> PaginatedResponse:
    """Export endpoint — requires explicit export=true. Max 1000 rows."""
    if not export:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requires export=true")
    from datetime import date as datetype
    date_from_parsed = datetype.fromisoformat(date_from) if date_from else None
    date_to_parsed = datetype.fromisoformat(date_to) if date_to else None
    filters = TransactionFilters(date_from=date_from_parsed, date_to=date_to_parsed)
    pagination = PaginationParams(page=1, pagesize=1000)
    service = TransactionService(session)
    return await service.get_user_transactions(current_user.id, filters, pagination)


@router.get("/{transaction_id}", response_model=TransactionDetail)
async def get_transaction(transaction_id: int, current_user: CurrentUser, session: DBSession) -> TransactionDetail:
    try:
        service = TransactionService(session)
        return await service.get_transaction(transaction_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: int, data: TransactionUpdate, current_user: CurrentUser, session: DBSession) -> TransactionResponse:
    try:
        service = TransactionService(session)
        return await service.update_transaction(transaction_id, current_user.id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: int, current_user: CurrentUser, session: DBSession) -> None:
    try:
        service = TransactionService(session)
        await service.delete_transaction(transaction_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
```
</document>

<document path="./src/api/v1/__init__.py">
```py
"""
API v1 endpoints.
"""

```
</document>

<document path="./src/api/deps.py">
```py
"""
API dependencies.
"""
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.exceptions import AuthenticationError
from src.models.user import User
from src.services.auth_service import AuthService


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        authorization: Authorization header (Bearer token)
        session: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token and get user
    try:
        auth_service = AuthService(session)
        user = await auth_service.get_current_user(token)
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_async_session)]

```
</document>

<document path="./src/app.py">
```py
"""FastAPI application factory with security hardening (SEC-04, SEC-09)."""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.v1.router import api_router
from src.config import settings
from src.core.cache import cache
from src.core.database import close_db, init_db
from src.core.exceptions import AutoFlowException
from src.core.logging import get_logger, setup_logging
from src.services.notify_listener_service import listen_for_transactions

setup_logging()
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response (SEC-09)."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting AutoFlow Backend", version=settings.APP_VERSION)
    await init_db()
    await cache.connect()
    listener_task = asyncio.create_task(listen_for_transactions())
    yield
    listener_task.cancel()
    try:
        await listener_task
    except asyncio.CancelledError:
        pass
    await cache.disconnect()
    await close_db()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
    )

    # SEC-09: Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # SEC-04: Explicit CORS methods and headers (no wildcards)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    # SEC-02: Rate limiter state
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.exception_handler(AutoFlowException)
    async def autoflow_exception_handler(request: Request, exc: AutoFlowException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "error_data": exc.detail},
        )

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": settings.APP_VERSION, "environment": settings.ENVIRONMENT}

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
```
</document>

<document path="./src/config.py">
```py
"""
Application configuration using Pydantic Settings.
"""
from functools import lru_cache
from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "AutoFlow Finance Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins."""
        if isinstance(v, str):
            # Если строка начинается с [, парсим как JSON
            if v.startswith("["):
                import json
                return json.loads(v)
            # Иначе разбиваем по запятой
            return [i.strip() for i in v.split(",")]
        return v

    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must start with postgresql:// or postgresql+asyncpg://")
        return v

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format."""
        if not v:
            raise ValueError("REDIS_URL cannot be empty")
        if not v.startswith("redis://"):
            raise ValueError("REDIS_URL must start with redis://")
        return v

    # Security
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    @field_validator("CELERY_BROKER_URL", "CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def validate_celery_url(cls, v: str) -> str:
        """Validate Celery Redis URL format."""
        if not v:
            raise ValueError("Celery URL cannot be empty")
        if not v.startswith("redis://"):
            raise ValueError("Celery URL must start with redis://")
        return v

    # LLM
    LLM_PROVIDER: Literal["openai", "anthropic", "ollama"] = "openai"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    OLLAMA_BASE_URL: str | None = None

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"

    # Telegram
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_BOT_USERNAME: str

    # ── Pipeline feature flags (для отладки) ──────────────────────────
    PIPELINE_RULE_ENGINE: bool = True     # вкл/выкл rule engine
    PIPELINE_LLM: bool = False            # вкл/выкл LLM-обогащение (дорого, по умолчанию OFF)
    PIPELINE_SETTLEMENT: bool = True      # вкл/выкл детектор взаимозачётов
    PIPELINE_LOG_VERBOSE: bool = True    # подробные логи каждого шага pipeline

@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

```
</document>

<document path="./src/repositories/habit_repo.py">
```py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import date
from src.models.habit import Habit
from src.repositories.base import BaseRepository

class HabitRepository(BaseRepository[Habit]):
    def __init__(self, session: AsyncSession):
        super().__init__(Habit, session)

    async def get_user_habits_with_logs(self, user_id: int, start_date: date) -> list[Habit]:
        stmt = (
            select(Habit)
            .where(Habit.user_id == user_id)
            # Обычный selectinload, который подгружает все логи
            .options(selectinload(Habit.logs))
        )
        result = await self.session.execute(stmt)
        habits = list(result.scalars().all())
        
        # Фильтруем логи программно в памяти
        for habit in habits:
            habit.logs = [log for log in habit.logs if log.date >= start_date]
            
        return habits
```
</document>

<document path="./src/repositories/user_repo.py">
```py
"""
User repository.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User instance or None
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User instance or None
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str, exclude_id: int | None = None) -> bool:
        """
        Check if email is already taken.
        
        Args:
            email: Email to check
            exclude_id: User ID to exclude from check (for updates)
            
        Returns:
            True if email exists, False otherwise
        """
        query = select(User).where(User.email == email)
        
        if exclude_id is not None:
            query = query.where(User.id != exclude_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def username_exists(
        self, username: str, exclude_id: int | None = None
    ) -> bool:
        """
        Check if username is already taken.
        
        Args:
            username: Username to check
            exclude_id: User ID to exclude from check (for updates)
            
        Returns:
            True if username exists, False otherwise
        """
        query = select(User).where(User.username == username)
        
        if exclude_id is not None:
            query = query.where(User.id != exclude_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get all active users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of active users
        """
        result = await self.session.execute(
            select(User)
            .where(User.is_active == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

```
</document>

<document path="./src/repositories/category_repo.py">
```py
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

```
</document>

<document path="./src/repositories/transaction_repo.py">
```py
"""
Transaction repository.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.transaction import Transaction
from src.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction model."""

    def __init__(self, session: AsyncSession):
        super().__init__(Transaction, session)

    async def get_user_transactions(
        self,
        user_id: int,
        account_id: int | None = None,
        category_id: int | None = None,
        transaction_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        search: str | None = None,   # ← ДОБАВЛЕНО
        skip: int = 0,
        limit: int = 100,
    ) -> list[Transaction]:
        from src.models.account import Account

        query = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .options(
                selectinload(Transaction.account),
                selectinload(Transaction.category),
                selectinload(Transaction.target_account),
            )
        )

        if account_id:
            query = query.where(Transaction.account_id == account_id)
        if category_id:
            query = query.where(Transaction.category_id == category_id)
        if transaction_type:
            query = query.where(Transaction.transaction_type == transaction_type)
        if date_from:
            query = query.where(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.where(Transaction.transaction_date <= date_to)

        # ← ДОБАВЛЕНО: поиск по merchant, description, notes
        if search:
            term = f"%{search}%"
            query = query.where(
                or_(
                    Transaction.merchant.ilike(term),
                    Transaction.description.ilike(term),
                    Transaction.notes.ilike(term),
                )
            )

        query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_total_by_type(
        self,
        user_id: int,
        transaction_type: str,
        date_from: date | None = None,
        date_to: date | None = None,
        account_id: int | None = None,
    ) -> Decimal:
        """
        Get total amount by transaction type.
        
        Args:
            user_id: User ID
            transaction_type: Transaction type
            date_from: Start date
            date_to: End date
            account_id: Filter by account
            
        Returns:
            Total amount
        """
        from src.models.account import Account
        
        query = (
            select(func.sum(Transaction.amount))
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .where(Transaction.transaction_type == transaction_type)
        )
        
        if date_from:
            query = query.where(Transaction.transaction_date >= date_from)
        
        if date_to:
            query = query.where(Transaction.transaction_date <= date_to)
        
        if account_id:
            query = query.where(Transaction.account_id == account_id)
        
        result = await self.session.execute(query)
        total = result.scalar_one_or_none()
        return total if total is not None else Decimal("0.00")

    async def get_by_category(
        self,
        user_id: int,
        category_id: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[Transaction]:
        """
        Get transactions by category.
        
        Args:
            user_id: User ID
            category_id: Category ID
            date_from: Start date
            date_to: End date
            
        Returns:
            List of transactions
        """
        from src.models.account import Account
        
        query = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .where(Transaction.category_id == category_id)
        )
        
        if date_from:
            query = query.where(Transaction.transaction_date >= date_from)
        
        if date_to:
            query = query.where(Transaction.transaction_date <= date_to)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search_transactions(
        self,
        user_id: int,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Transaction]:
        """
        Search transactions by description or merchant.
        
        Args:
            user_id: User ID
            search_term: Search term
            skip: Offset
            limit: Limit
            
        Returns:
            List of transactions
        """
        from src.models.account import Account
        
        query = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .where(
                or_(
                    Transaction.description.ilike(f"%{search_term}%"),
                    Transaction.merchant.ilike(f"%{search_term}%"),
                    Transaction.notes.ilike(f"%{search_term}%"),
                )
            )
            .order_by(Transaction.transaction_date.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recent_transactions(
        self, user_id: int, limit: int = 10
    ) -> list[Transaction]:
        """
        Get recent transactions for user.
        
        Args:
            user_id: User ID
            limit: Number of transactions
            
        Returns:
            List of recent transactions
        """
        from src.models.account import Account
        
        query = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .options(
                selectinload(Transaction.account),
                selectinload(Transaction.category),
            )
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_user_transactions(
        self,
        user_id: int,
        account_id: int | None = None,
        category_id: int | None = None,
        transaction_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        search: str | None = None,   # ← ДОБАВЛЕНО
    ) -> int:
        from src.models.account import Account

        query = (
            select(func.count(Transaction.id))
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
        )
        if account_id:
            query = query.where(Transaction.account_id == account_id)
        if category_id:
            query = query.where(Transaction.category_id == category_id)
        if transaction_type:
            query = query.where(Transaction.transaction_type == transaction_type)
        if date_from:
            query = query.where(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.where(Transaction.transaction_date <= date_to)

        # ← ДОБАВЛЕНО
        if search:
            term = f"%{search}%"
            query = query.where(
                or_(
                    Transaction.merchant.ilike(term),
                    Transaction.description.ilike(term),
                    Transaction.notes.ilike(term),
                )
            )

        result = await self.session.execute(query)
        return result.scalar_one()

```
</document>

<document path="./src/repositories/account_repo.py">
```py
"""
Account repository.
"""
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account import Account
from src.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """Repository for Account model."""

    def __init__(self, session: AsyncSession):
        super().__init__(Account, session)

    async def get_user_accounts(
        self,
        user_id: int,
        include_inactive: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Account]:
        """
        Get all accounts for a user.
        
        Args:
            user_id: User ID
            include_inactive: Include inactive accounts
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of accounts
        """
        query = select(Account).where(Account.user_id == user_id)
        
        if not include_inactive:
            query = query.where(Account.is_active == True)  # noqa: E712
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_total_balance(
        self, user_id: int, currency: str = "RUB"
    ) -> Decimal:
        """
        Calculate total balance for user's accounts.
        
        Args:
            user_id: User ID
            currency: Currency filter
            
        Returns:
            Total balance
        """
        result = await self.session.execute(
            select(func.sum(Account.balance))
            .where(Account.user_id == user_id)
            .where(Account.currency == currency)
            .where(Account.is_active == True)  # noqa: E712
            .where(Account.include_in_total == True)  # noqa: E712
        )
        total = result.scalar_one_or_none()
        return total if total is not None else Decimal("0.00")

    async def get_by_type(
        self, user_id: int, account_type: str
    ) -> list[Account]:
        """
        Get accounts by type for a user.
        
        Args:
            user_id: User ID
            account_type: Account type
            
        Returns:
            List of accounts
        """
        result = await self.session.execute(
            select(Account)
            .where(Account.user_id == user_id)
            .where(Account.account_type == account_type)
            .where(Account.is_active == True)  # noqa: E712
        )
        return list(result.scalars().all())

    async def update_balance(
        self, account_id: int, amount: Decimal, operation: str = "add"
    ) -> Account | None:
        """
        Update account balance.
        
        Args:
            account_id: Account ID
            amount: Amount to add or subtract
            operation: 'add' or 'subtract'
            
        Returns:
            Updated account or None
        """
        account = await self.get_by_id(account_id)
        
        if account is None:
            return None
        
        if operation == "add":
            new_balance = account.balance + amount
        elif operation == "subtract":
            new_balance = account.balance - amount
        else:
            raise ValueError(f"Invalid operation: {operation}")
        
        if new_balance < 0:
            raise ValueError("Account balance cannot be negative")
        
        return await self.update(account_id, balance=new_balance)

    async def get_balances_by_currency(self, user_id: int) -> dict[str, Decimal]:
        """Суммы по каждой валюте для активных счетов пользователя."""
        result = await self.session.execute(
            select(Account.currency, func.sum(Account.balance))
            .where(Account.user_id == user_id)
            .where(Account.is_active == True)
            .where(Account.include_in_total == True)
            .group_by(Account.currency)
        )
        return {row[0]: (row[1] or Decimal("0.00")) for row in result.all()}

    async def get_by_account_number(
        self, user_id: int, account_number: str
    ) -> Account | None:
        """Поиск счёта по полному номеру."""
        result = await self.session.execute(
            select(Account).where(
                Account.user_id        == user_id,
                Account.account_number == account_number,
            )
        )
        return result.scalar_one_or_none()


    async def get_by_last_four(
        self, user_id: int, last4: str
    ) -> Account | None:
        """Поиск карты/счёта по последним 4 цифрам (только card/bank_account)."""
        result = await self.session.execute(
            select(Account).where(
                Account.user_id.in_([user_id]),
                Account.last_four_digits == last4,
                Account.account_type.in_(["card", "bank_account"]),
                Account.is_active == True,
            )
        )
        return result.scalar_one_or_none()


    async def update_account_number(
        self, account_id: int, account_number: str
    ) -> None:
        """Обновить полный номер счёта — вызывается из ImportService."""
        await self.session.execute(
            text("""
                UPDATE finances.accounts
                SET account_number = :account_number,
                    updated_at     = NOW()
                WHERE id = :id
            """),
            {"account_number": account_number, "id": account_id},
        )
```
</document>

<document path="./src/repositories/base.py">
```py
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

```
</document>

<document path="./src/repositories/habit_log_repo.py">
```py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.habit_log import HabitLog
from src.repositories.base import BaseRepository
from datetime import date

class HabitLogRepository(BaseRepository[HabitLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(HabitLog, session)

    async def get_by_habit_and_date(self, habit_id: int, log_date: date) -> HabitLog | None:
        stmt = select(HabitLog).where(HabitLog.habit_id == habit_id, HabitLog.date == log_date)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```
</document>

<document path="./src/repositories/budget_repo.py">
```py
"""
Budget repository.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.budget import Budget
from src.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    """Repository for Budget model."""

    def __init__(self, session: AsyncSession):
        super().__init__(Budget, session)

    async def get_user_budgets(
        self, user_id: int, active_only: bool = True
    ) -> list[Budget]:
        """
        Get all budgets for user.
        
        Args:
            user_id: User ID
            active_only: Only active budgets (within date range)
            
        Returns:
            List of budgets
        """
        query = select(Budget).where(Budget.user_id == user_id)
        
        if active_only:
            today = date.today()
            query = query.where(
                and_(
                    Budget.start_date <= today,
                    or_(Budget.end_date.is_(None), Budget.end_date >= today),
                )
            )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_category(
        self, user_id: int, category_id: int
    ) -> Budget | None:
        """
        Get budget for specific category.
        
        Args:
            user_id: User ID
            category_id: Category ID
            
        Returns:
            Budget or None
        """
        result = await self.session.execute(
            select(Budget)
            .where(Budget.user_id == user_id)
            .where(Budget.category_id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_spent_amount(
        self, budget_id: int, start_date: date, end_date: date | None = None
    ) -> Decimal:
        """
        Calculate spent amount for budget period.
        
        Args:
            budget_id: Budget ID
            start_date: Period start
            end_date: Period end
            
        Returns:
            Spent amount
        """
        from src.models.transaction import Transaction
        
        budget = await self.get_by_id(budget_id)
        if not budget:
            return Decimal("0.00")
        
        query = (
            select(func.sum(Transaction.amount))
            .where(Transaction.transaction_type == "expense")
            .where(Transaction.transaction_date >= start_date)
        )
        
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)
        
        if budget.category_id:
            query = query.where(Transaction.category_id == budget.category_id)
        
        result = await self.session.execute(query)
        total = result.scalar_one_or_none()
        return total if total is not None else Decimal("0.00")

```
</document>

<document path="./src/repositories/search_sanitizer.py">
```py
"""Search term sanitizer to prevent wildcard injection (SEC-07)."""


def sanitize_search(term: str) -> str:
    """
    Sanitize search term for ILIKE queries.
    - Truncate to 100 chars
    - Escape backslashes (SQLAlchemy ILIKE wildcard escape)
    - Strip leading/trailing whitespace
    """
    if not term:
        return ""
    term = term[:100].strip()
    term = term.replace("\\", "\\\\")  # escape backslash
    return term
```
</document>

<document path="./src/repositories/__init__.py">
```py
"""
Data access layer - Repository pattern.
"""
from src.repositories.account_repo import AccountRepository
from src.repositories.budget_repo import BudgetRepository
from src.repositories.category_repo import CategoryRepository
from src.repositories.transaction_repo import TransactionRepository
from src.repositories.user_repo import UserRepository

__all__ = [
    "UserRepository",
    "AccountRepository",
    "CategoryRepository",
    "TransactionRepository",
    "BudgetRepository",
]

```
</document>

<document path="./src/core/database.py">
```py
"""
Async SQLAlchemy database setup.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.models.base import Base  # ← Импортируем Base из models

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """Initialize database (create all tables)."""
    # Импортируем все модели чтобы они зарегистрировались в MetaData
    from src.models.user import User          # [web:17]
    from src.models.account import Account    # [web:22]
    from src.models.category import Category  # [web:22]
    from src.models.transaction import Transaction  # [web:22]
    from src.models.budget import Budget      # если есть такая модель

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()

```
</document>

<document path="./src/core/security.py">
```py
"""
Security utilities: JWT tokens, password hashing.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str | Any) -> str:
    """Create JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify JWT token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

```
</document>

<document path="./src/core/exceptions.py">
```py
"""
Custom application exceptions.
"""
from typing import Any


class AutoFlowException(Exception):
    """Base exception."""
    def __init__(self, message: str = "An error occurred", status_code: int = 500, detail: Any = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class AuthenticationError(AutoFlowException):
    """Authentication failed."""
    def __init__(self, message: str = "Authentication failed", detail: Any = None):
        super().__init__(message=message, status_code=401, detail=detail)


class AuthorizationError(AutoFlowException):
    """Not authorized."""
    def __init__(self, message: str = "Not authorized", detail: Any = None):
        super().__init__(message=message, status_code=403, detail=detail)


class NotFoundError(AutoFlowException):
    """Resource not found."""
    def __init__(self, message: str = "Resource not found", detail: Any = None):
        super().__init__(message=message, status_code=404, detail=detail)


class ValidationError(AutoFlowException):
    """Validation error."""
    def __init__(self, message: str = "Validation error", detail: Any = None):
        super().__init__(message=message, status_code=422, detail=detail)


class ConflictError(AutoFlowException):
    """Resource conflict."""
    def __init__(self, message: str = "Resource conflict", detail: Any = None):
        super().__init__(message=message, status_code=409, detail=detail)

```
</document>

<document path="./src/core/cache.py">
```py
"""
Redis cache wrapper.
"""
import json
from typing import Any

from redis.asyncio import Redis

from src.config import settings


class RedisCache:
    """Async Redis cache wrapper."""

    def __init__(self) -> None:
        self.redis: Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self.redis = Redis.from_url(
            str(settings.REDIS_URL),
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Any:
        """Get value from cache."""
        if not self.redis:
            return None
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL) -> None:
        """Set value in cache with TTL."""
        if not self.redis:
            return
        await self.redis.setex(key, ttl, json.dumps(value, default=str))

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        if not self.redis:
            return
        await self.redis.delete(key)


cache = RedisCache()

```
</document>

<document path="./src/core/logging.py">
```py
"""Logging setup with PII redaction filter (SEC-11)."""
import logging
import structlog

SENSITIVE_FIELDS = {
    "password", "hashed_password", "access_token", "refresh_token",
    "token", "merchant", "account_number", "telegram_id",
    "auth_code", "card_number", "phone",
}


def redact_sensitive(logger, method, event_dict: dict) -> dict:
    """structlog processor: replace sensitive field values with ***REDACTED***."""
    for key in list(event_dict.keys()):
        if key.lower() in SENSITIVE_FIELDS:
            event_dict[key] = "***REDACTED***"
    return event_dict


def setup_logging() -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            redact_sensitive,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    logging.basicConfig(level=logging.INFO)


def get_logger(name: str = __name__):
    return structlog.get_logger(name)
```
</document>

<document path="./src/schemas/analytics.py">
```py
"""
Analytics Pydantic schemas.
"""
from datetime import date
from decimal import Decimal
from typing import Literal

from src.schemas.base import BaseSchema


TimeGrouping = Literal["day", "week", "month", "year"]


class TimeSeriesPoint(BaseSchema):
    """Точка временного ряда."""
    
    date: str  # ISO format or period (YYYY-MM)
    income: Decimal = Decimal("0.00")
    expense: Decimal = Decimal("0.00")
    net: Decimal = Decimal("0.00")
    balance: Decimal | None = None


class CategoryAnalytics(BaseSchema):
    """Аналитика по категории."""
    
    category_id: int
    category_name: str
    total_amount: Decimal
    transaction_count: int
    percentage: float
    average_amount: Decimal
    max_amount: Decimal
    min_amount: Decimal


class AccountAnalytics(BaseSchema):
    """Аналитика по счёту."""
    
    account_id: int
    account_name: str
    starting_balance: Decimal
    ending_balance: Decimal
    total_income: Decimal
    total_expense: Decimal
    transaction_count: int


class SpendingPattern(BaseSchema):
    """Паттерн расходов."""
    
    pattern_type: str  # daily_average, weekly_peak, monthly_trend
    value: Decimal
    description: str


class FinancialHealthScore(BaseSchema):
    """Оценка финансового здоровья."""
    
    score: int  # 0-100
    savings_rate: float  # percentage
    expense_volatility: float
    budget_adherence: float
    recommendations: list[str]


class AnalyticsReport(BaseSchema):
    """Полный аналитический отчёт."""
    
    period_start: date
    period_end: date
    
    time_series: list[TimeSeriesPoint]
    
    top_expense_categories: list[CategoryAnalytics]
    top_income_categories: list[CategoryAnalytics]
    
    account_performance: list[AccountAnalytics]
    
    spending_patterns: list[SpendingPattern]
    health_score: FinancialHealthScore

```
</document>

<document path="./src/schemas/dashboard.py">
```py
"""
Dashboard Pydantic schemas.
"""
from datetime import date
from decimal import Decimal

from src.schemas.account import AccountResponse
from src.schemas.base import BaseSchema
from src.schemas.transaction import TransactionResponse


class BalanceOverview(BaseSchema):
    """Обзор баланса."""
    
    total_balance: Decimal
    currency: str = "RUB"
    change_amount: Decimal = Decimal("0.00")
    change_percentage: float = 0.0
    account_count: int = 0


class IncomeExpenseSummary(BaseSchema):
    """Сводка доходов/расходов."""
    
    total_income: Decimal = Decimal("0.00")
    total_expense: Decimal = Decimal("0.00")
    net_amount: Decimal = Decimal("0.00")
    income_count: int = 0
    expense_count: int = 0


class CategorySummary(BaseSchema):
    """Сводка по категории."""
    
    category_id: int
    category_name: str
    category_type: str
    total_amount: Decimal
    transaction_count: int
    percentage: float = 0.0


class MonthlyComparison(BaseSchema):
    """Сравнение по месяцам."""
    
    month: str  # YYYY-MM
    income: Decimal
    expense: Decimal
    net: Decimal


class DashboardData(BaseSchema):
    """Полные данные для дашборда."""
    
    period_start: date
    period_end: date
    
    balance: BalanceOverview
    income_expense: IncomeExpenseSummary
    
    top_accounts: list[AccountResponse]
    recent_transactions: list[TransactionResponse]
    
    expense_by_category: list[CategorySummary]
    income_by_category: list[CategorySummary]
    
    monthly_trend: list[MonthlyComparison]

```
</document>

<document path="./src/schemas/telegram.py">
```py
"""
Telegram schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class GenerateLinkResponse(BaseModel):
    """Ответ на генерацию deep link."""
    deep_link: str        
    token: str           
    expires_at: datetime


class TelegramLinkRequest(BaseModel):
    """n8n отправляет этот запрос после /start auth_TOKEN."""
    token: str
    telegram_id: int
    telegram_username: Optional[str] = None


class TelegramLinkResponse(BaseModel):
    """Ответ на успешную привязку."""
    success: bool
    message: str
    username: Optional[str] = None  # имя пользователя на платформе


class TelegramStatusResponse(BaseModel):
    """Статус привязки Telegram для UI."""
    is_linked: bool
    telegram_username: Optional[str] = None
    telegram_id: Optional[int] = None

```
</document>

<document path="./src/schemas/user.py">
```py
"""User Pydantic schemas — full version with SEC-12 and SEC-13 fixes."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.schemas.base import BaseSchema, TimestampSchema


class UserBase(BaseSchema):
    email: EmailStr
    username: str
    full_name: str | None = None


class UserCreate(BaseModel):
    """Registration schema — used by AuthService."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    full_name: str | None = Field(None, max_length=255)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        import re
        if not re.match(r"^[a-zA-Z0-9_-]{3,100}$", v):
            raise ValueError("Username may only contain letters, digits, _ and -")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        errors = []
        if len(v) < 8:
            errors.append("минимум 8 символов")
        if not any(c.isupper() for c in v):
            errors.append("хотя бы одна заглавная буква")
        if not any(c.islower() for c in v):
            errors.append("хотя бы одна строчная буква")
        if errors:
            raise ValueError(f"Пароль должен содержать: {', '.join(errors)}")
        return v


class UserUpdate(BaseSchema):
    """Profile update schema.
    SEC-13: password removed — use POST /auth/change-password instead.
    """
    username: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=255)
    # NOTE: password intentionally omitted — use POST /auth/change-password


class UserResponse(UserBase, TimestampSchema):
    """Public user schema.
    SEC-12: is_superuser removed — use AdminUserResponse for internal use.
    """
    id: int
    is_active: bool
    telegram_id: int | None = None       # нужен в settings/page.tsx для отображения статуса
    telegram_username: str | None = None


class AdminUserResponse(UserResponse):
    """Internal admin schema — includes privileged fields (SEC-12)."""
    is_superuser: bool
    hashed_password: str | None = None   # только для отладки, никогда в API


class UserInDB(UserBase, TimestampSchema):
    """Internal schema with hashed password — never returned via API."""
    id: int
    is_active: bool
    is_superuser: bool
    hashed_password: str


class UserProfile(UserResponse):
    """Extended user profile with stats."""
    total_accounts: int = 0
    total_transactions: int = 0
```
</document>

<document path="./src/schemas/base.py">
```py
"""
Base Pydantic schemas.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Для работы с SQLAlchemy моделями
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamps."""
    
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    """Параметры пагинации."""
    
    page: int = 1
    page_size: int = 20
    
    @property
    def offset(self) -> int:
        """Вычислить offset для SQL."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Вычислить limit для SQL."""
        return self.page_size


class PaginatedResponse(BaseSchema):
    """Обёртка для пагинированных ответов."""
    
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(
        cls,
        items: list[Any],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse":
        """Создать пагинированный ответ."""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

```
</document>

<document path="./src/schemas/budget.py">
```py
"""
Budget Pydantic schemas.
"""
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from src.schemas.base import BaseSchema, TimestampSchema
from src.schemas.category import CategoryResponse


PeriodType = Literal["daily", "weekly", "monthly", "yearly"]


class BudgetBase(BaseSchema):
    """Базовые поля бюджета."""
    
    name: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0)
    period_type: PeriodType
    start_date: date
    end_date: date | None = None
    
    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: date | None, info) -> date | None:
        """Проверка что end_date > start_date."""
        if v is not None and "start_date" in info.data:
            if v <= info.data["start_date"]:
                raise ValueError("end_date must be after start_date")
        return v


class BudgetCreate(BudgetBase):
    """Схема создания бюджета."""
    
    category_id: int | None = None


class BudgetUpdate(BaseSchema):
    """Схема обновления бюджета."""
    
    name: str | None = Field(None, min_length=1, max_length=255)
    amount: Decimal | None = Field(None, gt=0)
    period_type: PeriodType | None = None
    start_date: date | None = None
    end_date: date | None = None
    category_id: int | None = None


class BudgetInDB(BudgetBase, TimestampSchema):
    """Бюджет из БД."""
    
    id: int
    user_id: int
    category_id: int | None


class BudgetResponse(BudgetBase, TimestampSchema):
    """Бюджет для API ответа."""
    
    id: int
    category_id: int | None


class BudgetWithStats(BudgetResponse):
    """Бюджет со статистикой использования."""
    
    category: CategoryResponse | None = None
    spent_amount: Decimal = Decimal("0.00")
    remaining_amount: Decimal = Decimal("0.00")
    spent_percentage: float = 0.0
    is_exceeded: bool = False
    days_remaining: int = 0

```
</document>

<document path="./src/schemas/category.py">
```py
"""
Category Pydantic schemas.
"""
from typing import Literal

from pydantic import Field

from src.schemas.base import BaseSchema, TimestampSchema


CategoryType = Literal["income", "expense", "transfer"]


class CategoryBase(BaseSchema):
    """Базовые поля категории."""
    
    name: str = Field(min_length=1, max_length=100)
    category_type: CategoryType
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryCreate(CategoryBase):
    """Схема создания категории."""
    pass


class CategoryUpdate(BaseSchema):
    """Схема обновления категории."""
    
    name: str | None = Field(None, min_length=1, max_length=100)
    category_type: CategoryType | None = None
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active: bool | None = None


class CategoryInDB(CategoryBase, TimestampSchema):
    """Категория из БД."""
    
    id: int
    user_id: int | None
    is_system: bool
    is_active: bool


class CategoryResponse(CategoryBase, TimestampSchema):
    """Категория для API ответа."""
    
    id: int
    is_system: bool
    is_active: bool


class CategoryWithStats(CategoryResponse):
    """Категория со статистикой использования."""
    
    transaction_count: int = 0
    total_amount: str = "0.00"  # Decimal as string for JSON

```
</document>

<document path="./src/schemas/account.py">
```py
"""
Account Pydantic schemas.
"""
"""
Account Pydantic schemas.
"""
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator, model_validator

from src.schemas.base import BaseSchema, TimestampSchema


AccountType = Literal["card", "bank_account", "cash"]

# Типы, создаваемые только автоимпортом
AUTO_IMPORT_TYPES = ("card", "bank_account")


class AccountBase(BaseSchema):
    """Базовые поля счёта — без ограничительных валидаторов."""

    name:             str         = Field(min_length=1, max_length=255)
    account_type:     AccountType
    currency:         str         = Field(default="RUB", max_length=3)
    bank_name:        str | None  = Field(None, max_length=255)
    last_four_digits: str | None  = Field(None, min_length=4, max_length=4)
    icon:             str | None  = Field(None, max_length=50)
    color:            str | None  = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    include_in_total: bool        = True

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        allowed = ["RUB", "USD", "EUR", "GBP", "CNY", "BTC", "ETH"]
        if v.upper() not in allowed:
            raise ValueError(f"Currency must be one of: {', '.join(allowed)}")
        return v.upper()


class AccountCreate(AccountBase):
    """
    Схема создания счёта.
    Вручную — только cash.
    card/bank_account создаются только через ImportService (минуя этот валидатор).
    """

    balance: Decimal = Field(default=Decimal("0.00"), ge=0)

    @field_validator("account_type")
    @classmethod
    def only_cash_allowed(cls, v: AccountType) -> AccountType:
        if v != "cash":
            raise ValueError(
                "Вручную можно создать только счёт наличных. "
                "Банковские карты и счета добавляются автоматически из выписки."
            )
        return v


class AccountUpdate(BaseSchema):
    """
    Схема обновления счёта.

    Разрешено пользователю:
    - name           — все типы
    - currency       — все типы
    - icon, color    — все типы
    - is_active      — все типы
    - include_in_total — все типы
    - bank_name      — только card/bank_account (проверяется в сервисе)
    - account_type   — только card ↔ bank_account (проверяется в сервисе)

    Запрещено (поля отсутствуют):
    - balance        — управляется транзакциями и импортом
    - last_four_digits — системное поле, ставится при импорте
    """

    name:             str | None         = Field(None, min_length=1, max_length=255)
    account_type:     AccountType | None = None
    currency:         str | None         = Field(None, max_length=3)
    bank_name:        str | None         = Field(None, max_length=255)
    icon:             str | None         = Field(None, max_length=50)
    color:            str | None         = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active:        bool | None        = None
    include_in_total: bool | None        = None
    balance: Decimal | None = Field(None, ge=0)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = ["RUB", "USD", "EUR", "GBP", "CNY", "BTC", "ETH"]
        if v.upper() not in allowed:
            raise ValueError(f"Currency must be one of: {', '.join(allowed)}")
        return v.upper()


class AccountInDB(AccountBase, TimestampSchema):
    """Счёт из БД."""

    id:        int
    user_id:   int
    balance:   Decimal
    is_active: bool


class AccountResponse(AccountBase, TimestampSchema):
    """Счёт для API ответа."""

    id:        int
    balance:   Decimal
    is_active: bool


class AccountWithStats(AccountResponse):
    """Счёт с дополнительной статистикой."""

    transaction_count:     int          = 0
    last_transaction_date: str | None   = None
    income_total:          Decimal      = Decimal("0.00")
    expense_total:         Decimal      = Decimal("0.00")

```
</document>

<document path="./src/schemas/transaction.py">
```py
"""
Transaction Pydantic schemas.
"""
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from src.schemas.account import AccountResponse
from src.schemas.base import BaseSchema, TimestampSchema
from src.schemas.category import CategoryResponse


TransactionType = Literal["income", "expense", "transfer"]

class AccountShort(BaseSchema):
    id: int
    name: str

class CategoryShort(BaseSchema):
    id: int
    name: str


class TransactionBase(BaseSchema):
    """Базовые поля транзакции."""
    
    account_id: int
    category_id: int | None = None
    transaction_date: date
    amount: Decimal = Field(gt=0)
    transaction_type: TransactionType
    description: str | None = Field(None, max_length=500)
    notes: str | None = None
    merchant: str | None = Field(None, max_length=255)
    location: str | None = Field(None, max_length=255)
    tags: str | None = Field(None, max_length=500)
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: str | None) -> str | None:
        """Валидация тегов (comma-separated)."""
        if v is None:
            return None
        # Удаляем лишние пробелы
        tags = [tag.strip() for tag in v.split(",")]
        return ", ".join([tag for tag in tags if tag])


class TransactionCreate(TransactionBase):
    """Схема создания транзакции."""
    
    target_account_id: int | None = None
    
    @field_validator("target_account_id")
    @classmethod
    def validate_transfer(cls, v: int | None, info) -> int | None:
        """Для переводов target_account_id обязателен."""
        if info.data.get("transaction_type") == "transfer" and v is None:
            raise ValueError("target_account_id required for transfer transactions")
        return v


class TransactionUpdate(BaseSchema):
    """Схема обновления транзакции."""
    
    account_id: int | None = None
    category_id: int | None = None
    transaction_date: date | None = None
    amount: Decimal | None = Field(None, gt=0)
    transaction_type: TransactionType | None = None
    description: str | None = Field(None, max_length=500)
    notes: str | None = None
    merchant: str | None = Field(None, max_length=255)
    location: str | None = Field(None, max_length=255)
    tags: str | None = Field(None, max_length=500)
    target_account_id: int | None = None


class TransactionInDB(TransactionBase, TimestampSchema):
    """Транзакция из БД."""
    
    id: int
    target_account_id: int | None


class TransactionResponse(TransactionBase, TimestampSchema):
    """Транзакция для API ответа."""
    
    id: int
    target_account_id: int | None
    account: AccountShort | None = None      # ← добавить
    category: CategoryShort | None = None


class TransactionDetail(TransactionResponse):
    """Детальная транзакция с relationships."""
    
    account: AccountResponse
    category: CategoryResponse | None = None
    target_account: AccountResponse | None = None


class TransactionFilters(BaseSchema):
    """Фильтры для поиска транзакций."""
    
    account_id: int | None = None
    category_id: int | None = None
    transaction_type: TransactionType | None = None
    date_from: date | None = None
    date_to: date | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    merchant: str | None = None
    search: str | None = None  # Поиск по description

```
</document>

<document path="./src/schemas/auth.py">
```py
"""
Authentication Pydantic schemas.
"""
import re
from typing import Optional
from pydantic import BaseModel, field_validator, EmailStr, Field
from src.schemas.base import BaseSchema
from src.schemas.user import UserResponse

EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
)
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_\-]{3,100}$')

def is_valid_email(value: str) -> bool:
    return bool(EMAIL_REGEX.match(value))


def is_valid_username(value: str) -> bool:
    return bool(USERNAME_REGEX.match(value))

class Token(BaseSchema):
    """JWT токен."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseSchema):
    """Payload JWT токена."""
    
    sub: str  # user_id
    exp: int
    type: str  # access | refresh

class LoginRequest(BaseModel):
    login:    str   # email или username — валидируется ниже
    password: str

    @field_validator('login')
    @classmethod
    def validate_login(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("Поле не может быть пустым")
        if '@' in v:
            if not EMAIL_REGEX.match(v):
                raise ValueError("Некорректный email. Ожидается формат: user@domain.com")
        else:
            if not USERNAME_REGEX.match(v):
                raise ValueError(
                    "Некорректный username. "
                    "Допускаются буквы, цифры, _ и -. "
                    "Длина от 3 до 100 символов"
                )
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Пароль не может быть пустым")
        return v

class RegisterRequest(BaseModel):
    email:     EmailStr  # Pydantic встроенный валидатор
    username:  str
    password:  str
    full_name: Optional[str] = None

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not is_valid_username(v):
            raise ValueError(
                "Username может содержать только буквы, цифры, _ и -. "
                "Длина от 3 до 100 символов"
            )
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        errors = []
        if len(v) < 8:
            errors.append("минимум 8 символов")
        if not re.search(r'[A-Z]', v):
            errors.append("минимум одна заглавная буква")
        if not re.search(r'[a-z]', v):
            errors.append("минимум одна строчная буква")
        if not re.search(r'\d', v):
            errors.append("минимум одна цифра")
        if errors:
            raise ValueError(f"Пароль должен содержать: {', '.join(errors)}")
        return v


class AuthResponse(BaseSchema):
    """Ответ после успешной аутентификации."""
    
    user: UserResponse
    tokens: Token


class RefreshTokenRequest(BaseSchema):
    """Запрос на обновление токена."""
    
    refresh_token: str


class PasswordChangeRequest(BaseSchema):
    """Запрос на смену пароля."""
    
    old_password: str
    new_password: str = Field(min_length=8, max_length=100)

```
</document>

<document path="./src/schemas/__init__.py">
```py
"""
Pydantic schemas for API validation and serialization.
"""
from src.schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    AccountWithStats,
)
from src.schemas.analytics import AnalyticsReport, CategoryAnalytics, TimeSeriesPoint
from src.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, Token
from src.schemas.base import PaginatedResponse, PaginationParams
from src.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate, BudgetWithStats
from src.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from src.schemas.dashboard import DashboardData, BalanceOverview, IncomeExpenseSummary
from src.schemas.transaction import (
    TransactionCreate,
    TransactionDetail,
    TransactionFilters,
    TransactionResponse,
    TransactionUpdate,
)
from src.schemas.user import UserCreate, UserProfile, UserResponse, UserUpdate

__all__ = [
    # Base
    "PaginationParams",
    "PaginatedResponse",
    # Auth
    "Token",
    "LoginRequest",
    "RegisterRequest",
    "AuthResponse",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    # Account
    "AccountCreate",
    "AccountUpdate",
    "AccountResponse",
    "AccountWithStats",
    # Category
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    # Transaction
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionResponse",
    "TransactionDetail",
    "TransactionFilters",
    # Budget
    "BudgetCreate",
    "BudgetUpdate",
    "BudgetResponse",
    "BudgetWithStats",
    # Dashboard
    "DashboardData",
    "BalanceOverview",
    "IncomeExpenseSummary",
    # Analytics
    "AnalyticsReport",
    "CategoryAnalytics",
    "TimeSeriesPoint",
]

```
</document>

<document path="./src/schemas/habit.py">
```py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date
from src.models.habit import HabitFrequency

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#3b82f6"
    icon: Optional[str] = "target"
    frequency: HabitFrequency = HabitFrequency.daily

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    frequency: Optional[HabitFrequency] = None
    current_streak: int = 0

class HabitLogResponse(BaseModel):
    id: int
    date: date
    is_completed: bool
    model_config = ConfigDict(from_attributes=True)

class HabitResponse(HabitBase):
    id: int
    user_id: int
    current_streak: int = 0
    logs: List[HabitLogResponse] = []
    model_config = ConfigDict(from_attributes=True)

```
</document>

<document path="./src/services/llm_privacy.py">
```py
"""LLM Privacy Layer — sanitizes PII before sending to LLM."""
import hmac
import hashlib
import re
from typing import Any

PATTERNS: dict[str, str] = {
    "person_transfer": r"Перевод (?:для|от) ([А-ЯЁ]\.\s[А-ЯЁ][а-яё]+(?:\s[А-ЯЁ][а-яё]+)?)",
    "account_number": r"\b(\d{16,20})\b",
    "card_last4": r"\*{2,4}(\d{4})",
    "phone": r"(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",
    "full_name": r"\b([А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+)\b",
}

LLM_ALLOWED_FIELDS = {"date", "amount", "tx_type", "bank_category", "merchant", "balance"}
LLM_BLOCKED_FIELDS = {"telegram_id", "account_number", "auth_code", "user_id", "hashed_password"}


def _hmac_token(value: str, salt: bytes, prefix: str) -> str:
    """Deterministic 4-char HMAC token for a given value + salt."""
    digest = hmac.new(salt, value.lower().strip().encode(), hashlib.sha256).hexdigest()
    return f"[{prefix}_{digest[:4]}]"


def sanitize_for_llm(transaction: dict, user_salt: bytes) -> tuple[dict, dict]:
    """
    Replace PII in transaction with deterministic tokens.
    Returns (sanitized_tx, token_map).
    token_map is keyed by token string -> original value (session-only, never persisted).
    """
    token_map: dict[str, str] = {}
    sanitized = {k: v for k, v in transaction.items() if k in LLM_ALLOWED_FIELDS}

    merchant: str = sanitized.get("merchant") or ""

    # person_transfer — named groups
    def replace_person_transfer(m: re.Match) -> str:
        name = m.group(1)
        token = _hmac_token(name, user_salt, "PERSON")
        token_map[token] = name
        return m.group(0).replace(name, token)

    merchant = re.sub(PATTERNS["person_transfer"], replace_person_transfer, merchant)

    # full_name (ФИО) — standalone
    def replace_full_name(m: re.Match) -> str:
        name = m.group(1)
        token = _hmac_token(name, user_salt, "PERSON")
        token_map[token] = name
        return token

    merchant = re.sub(PATTERNS["full_name"], replace_full_name, merchant)

    # account_number
    def replace_account(m: re.Match) -> str:
        acc = m.group(1)
        token = _hmac_token(acc, user_salt, "ACCOUNT")
        token_map[token] = acc
        return token

    merchant = re.sub(PATTERNS["account_number"], replace_account, merchant)

    # card_last4
    def replace_card(m: re.Match) -> str:
        last4 = m.group(1)
        token = f"[CARD_{last4}]"
        token_map[token] = m.group(0)
        return token

    merchant = re.sub(PATTERNS["card_last4"], replace_card, merchant)

    # phone
    def replace_phone(m: re.Match) -> str:
        phone = m.group(0)
        token = _hmac_token(phone, user_salt, "PHONE")
        token_map[token] = phone
        return token

    merchant = re.sub(PATTERNS["phone"], replace_phone, merchant)

    sanitized["merchant"] = merchant
    return sanitized, token_map


def prepare_batch_for_llm(
    transactions: list[dict], user_salt: bytes
) -> tuple[list[dict], dict]:
    """
    Sanitize a list of transactions for LLM.
    Returns (sanitized_list, merged_token_map).
    """
    result: list[dict] = []
    merged_token_map: dict[str, str] = {}

    for tx in transactions:
        # Strip blocked fields first
        clean_tx = {k: v for k, v in tx.items() if k not in LLM_BLOCKED_FIELDS}
        sanitized, token_map = sanitize_for_llm(clean_tx, user_salt)
        merged_token_map.update(token_map)
        result.append(sanitized)

    return result, merged_token_map


LLM_SYSTEM_PROMPT = """You are a financial transaction classifier. You receive sanitized transaction data where personal identifiers have been replaced with tokens like [PERSON_xxxx], [ACCOUNT_xxxx].
DO NOT attempt to reconstruct or guess the original values behind these tokens.
Classify each transaction based only on merchant name patterns and amount context.

Respond ONLY with valid JSON. No explanations, no markdown blocks."""

LLM_USER_PROMPT_TEMPLATE = """Classify the following transaction:
{{
  "date": "{date}",
  "amount": {amount},
  "tx_type": "{tx_type}",
  "bank_category": "{bank_category}",
  "merchant": "{merchant}"
}}

Respond with:
{{
  "enriched_category": "<category from list>",
  "income_type": "<operational|oneoff|return|internal|null>",
  "expense_type": "<regular|subscription|oneoff|investment|debt_payment|null>",
  "is_internal_transfer": <true|false>,
  "exclude_from_metrics": <true|false>,
  "is_group_payment_suspect": <true|false>,
  "confidence": <0.0-1.0>,
  "needs_user_review": <true|false>,
  "review_reason": "<short reason or null>"
}}

Allowed enriched_category values:
"Зарплата", "Фриланс", "Возврат", "Кэшбэк", "Продукты", "Рестораны",
"Транспорт", "Такси", "Подписки", "Связь", "Одежда", "Здоровье",
"Развлечения", "Путешествия", "Обязательные платежи", "Переводы (регулярные)",
"Переводы (долги)", "Инвестиции", "Внутренний перевод", "Донаты", "Прочее"
"""


def build_llm_prompt(sanitized_tx: dict) -> str:
    return LLM_USER_PROMPT_TEMPLATE.format(
        date=sanitized_tx.get("date", ""),
        amount=sanitized_tx.get("amount", 0),
        tx_type=sanitized_tx.get("tx_type", ""),
        bank_category=sanitized_tx.get("bank_category", ""),
        merchant=sanitized_tx.get("merchant", ""),
    )
```
</document>

<document path="./src/services/import_service.py">
```py
"""
Import Service — обрабатывает транзакции из bot.finance_transactions.
"""
from decimal import Decimal
from datetime import date, datetime, timezone
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.models.user import User
from src.models.transaction import Transaction
from src.schemas.account import AccountResponse
from src.services.account_service import AccountService
from src.services.category_service import CategoryService
from src.services.enrichment_service import enrich_transactions
from src.services.settlement_detector import detect_settlements, extract_contact_ref
from src.config import settings

logger = logging.getLogger(__name__)


class ImportService:

    def __init__(self, session: AsyncSession):
        self.session          = session
        self.account_service  = AccountService(session)
        self.category_service = CategoryService(session)

    # ------------------------------------------------------------------ #
    # Точка входа                                                          #
    # ------------------------------------------------------------------ #

    async def process_pending(self, telegram_id: int) -> int:
        """
        Обрабатывает все pending записи пользователя.
        Возвращает количество импортированных транзакций.
        """
        logger.info(f"process_pending вызван для telegram_id={telegram_id}")
        user = await self._get_user_by_telegram(telegram_id)
        if not user:
            logger.warning(f"Пользователь с telegram_id={telegram_id} не найден")
            return 0

        rows = await self.session.execute(
            text("""
                SELECT id, account_number, date_msk, time_msk,
                       auth_code, category, amount, tx_type,
                       balance, date_operation, merchant
                FROM bot.finance_transactions
                WHERE telegram_id   = :telegram_id
                  AND import_status = 'pending'
                ORDER BY date_msk, time_msk
            """),
            {"telegram_id": telegram_id},
        )
        pending = rows.mappings().all()

        if not pending:
            return 0

        imported = 0
        last_balances: dict[str, Decimal] = {}
        imported_txs = []
        
        for row in pending:
            try:
                tx = await self._process_row(user, dict(row))
                if tx:
                    imported_txs.append(tx)
                await self.session.execute(
                    text("""
                        UPDATE bot.finance_transactions
                        SET import_status = 'done', imported_at = NOW()
                        WHERE id = :id
                    """),
                    {"id": row["id"]},
                )
                imported += 1
                acc_num = row.get("account_number", "")
                if row.get("balance") is not None:
                    last_balances[acc_num] = Decimal(str(row.get("balance", 0)))
            except Exception as e:
                logger.error(f"Ошибка импорта строки id={row['id']}: {e}")
                await self.session.execute(
                    text("UPDATE bot.finance_transactions SET import_status = 'error' WHERE id = :id"),
                    {"id": row["id"]},
                )

        # Финальное обновление балансов — только ОДИН раз, через raw SQL
        # Минуем ORM-кэш полностью
        for account_number, final_balance in last_balances.items():
            logger.info(f"Updating balance for {account_number}: {final_balance}")
            await self.session.execute(
                text("""
                    UPDATE finances.accounts
                    SET balance = :balance, updated_at = NOW()
                    WHERE account_number = :account_number
                      AND user_id = :user_id
                """),
                {
                    "balance": final_balance,
                    "account_number": account_number,
                    "user_id": user.id,
                },
            )

        await self.session.commit()

        # ── Ensure user_keys salt exists ──────────────────────────
        await self._ensure_user_salt(telegram_id)

        # ── Phase 1: Rule Engine ──────────────────────────────────
        if settings.PIPELINE_RULE_ENGINE and imported_txs:
            if settings.PIPELINE_LOG_VERBOSE:
                logger.info(f"[PIPELINE] Rule engine: {len(imported_txs)} transactions")
            await enrich_transactions(self.session, imported_txs, telegram_id)

        # ── Phase 2: Settlement Detector ─────────────────────────
        if settings.PIPELINE_SETTLEMENT and imported_txs:
            tx_dicts = [
                {"id": tx.id, "merchant": tx.merchant, "txtype": tx.transaction_type,
                 "amount": str(tx.amount), "date": str(tx.transaction_date)}
                for tx in imported_txs
            ]
            from src.services.settlement_detector import detect_settlements
            salt = await self._get_salt_bytes(telegram_id)
            pairs = detect_settlements(tx_dicts, salt)
            if pairs and settings.PIPELINE_LOG_VERBOSE:
                logger.info(f"[PIPELINE] Settlement pairs found: {len(pairs)}")

        logger.info(f"Импортировано {imported} транзакций для telegram_id={telegram_id}")
        return imported
    # ------------------------------------------------------------------ #
    # Обработка одной строки                                               #
    # ------------------------------------------------------------------ #

    async def _process_row(self, user: User, row: dict) -> None:
        if row.get("auth_code"):
            dup = await self.session.execute(
                select(Transaction).where(
                    Transaction.user_id == user.id,
                    Transaction.external_id == row["auth_code"],
                )
            )
            if dup.scalar_one_or_none():
                return None

        account = await self._resolve_account(user, row)
        category = await self._resolve_category(user, row)

        tx_date = row["date_msk"]
        if isinstance(tx_date, str):
            tx_date = date.fromisoformat(tx_date)

        tx = Transaction(
            user_id=user.id,
            account_id=account.id,
            category_id=category.id if category else None,
            transaction_date=tx_date,
            amount=Decimal(str(row["amount"])),
            transaction_type=row["tx_type"],
            merchant=row.get("merchant"),
            external_id=row.get("auth_code"),
            import_source="sber_pdf",
        )
        self.session.add(tx)
        await self.session.flush()
        return tx
    # ------------------------------------------------------------------ #
    # Резолв счёта                                                         #
    # ------------------------------------------------------------------ #

    async def _resolve_account(self, user: User, row: dict) -> AccountResponse:
        """
        Ищет счёт по account_number.
        Если не найден — создаёт через AccountService.create_account_from_import.
        """
        account_number = row.get("account_number", "")
        last4 = account_number[-4:] if len(account_number) >= 4 else account_number

        # Ищем по точному номеру
        existing = await self.account_service.get_accounts_by_number(
            user.id, account_number
        )
        if existing:
            return existing

        # Ищем по последним 4 цифрам среди card/bank_account
        existing_by_last4 = await self.account_service.get_account_by_last4(
            user.id, last4
        )
        if existing_by_last4:
            # Сохраняем полный номер
            await self.account_service.update_account_number(
                existing_by_last4.id, account_number
            )
            return existing_by_last4

        # Создаём новый счёт
        return await self.account_service.create_account_from_import(
            user_id          = user.id,
            name             = f"Сбер ****{last4}",
            account_type     = "card",
            currency         = "RUB",
            balance          = Decimal(0),
            bank_name        = "Сбербанк",
            last_four_digits = last4,
            account_number   = account_number,
        )

    # ------------------------------------------------------------------ #
    # Резолв категории                                                     #
    # ------------------------------------------------------------------ #

    async def _resolve_category(self, user: User, row: dict):
        """
        Ищет категорию по имени среди пользовательских и системных.
        Если не найдена — создаёт автоматически.
        """
        category_name = row.get("category", "").strip()
        if not category_name:
            return None

        # Ищем среди существующих (включая системные)
        all_categories = await self.category_service.get_user_categories(
            user.id, include_system=True
        )
        for cat in all_categories:
            if cat.name.lower() == category_name.lower():
                return cat

        # Автосоздание
        from src.schemas.category import CategoryCreate
        new_cat = await self.category_service.create_category(
            user.id,
            CategoryCreate(
                name          = category_name,
                category_type = row.get("tx_type", "expense"),
            ),
        )
        return new_cat

    # ------------------------------------------------------------------ #
    # Вспомогательное                                                      #
    # ------------------------------------------------------------------ #

    async def _get_user_by_telegram(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


    # ------------------------------------------------------------------ #
    # Соль пользователей                                                 #
    # ------------------------------------------------------------------ #

    async def _ensure_user_salt(self, telegram_id: int) -> None:
        """Создаёт запись user_keys если её нет."""
        from sqlalchemy import text
        import secrets
        existing = await self.session.execute(
            text("SELECT id FROM finances.user_keys WHERE telegram_id = :tid"),
            {"tid": telegram_id},
        )
        if not existing.fetchone():
            salt = secrets.token_hex(32)  # 64-char hex
            await self.session.execute(
                text("INSERT INTO finances.user_keys (telegram_id, salt) VALUES (:tid, :salt)"),
                {"tid": telegram_id, "salt": salt},
            )
            await self.session.commit()
            logger.info(f"[PIPELINE] Created user_key salt for telegram_id={telegram_id}")

    async def _get_salt_bytes(self, telegram_id: int) -> bytes:
        from sqlalchemy import text
        result = await self.session.execute(
            text("SELECT salt FROM finances.user_keys WHERE telegram_id = :tid"),
            {"tid": telegram_id},
        )
        row = result.fetchone()
        if row:
            return bytes.fromhex(row[0]) if isinstance(row[0], str) else row[0]
        return settings.SECRET_KEY.encode()[:32]  # fallback

```
</document>

<document path="./src/services/category_service.py">
```py
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

```
</document>

<document path="./src/services/settlement_detector.py">
```py
"""Mutual settlement detection between transfer pairs."""
import hashlib
import hmac
import re
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

TRANSFER_PATTERN = re.compile(
    r"Перевод (?:для|от) ([А-ЯЁ]\.[\s][А-ЯЁ][а-яё]+(?:\s[А-ЯЁ][а-яё]+)?)"
)


@dataclass
class SettlementPair:
    expense_tx_id: int
    income_tx_id: int
    contact_ref: str
    net_amount: Decimal


def _contact_ref(name: str, user_salt: bytes) -> str:
    digest = hmac.new(user_salt, name.lower().strip().encode(), hashlib.sha256).hexdigest()
    return f"cnt_{digest[:16]}"


def extract_contact_ref(merchant: str, user_salt: bytes) -> str | None:
    m = TRANSFER_PATTERN.search(merchant or "")
    if m:
        return _contact_ref(m.group(1), user_salt)
    return None


def detect_settlements(
    transactions: list[dict],
    user_salt: bytes,
) -> list[SettlementPair]:
    """
    Find expense+income pairs with same contact_ref within ±7 days.
    Mutates transactions dicts: sets 'contact_ref'.
    """
    # Attach contact_ref to each tx
    for tx in transactions:
        ref = extract_contact_ref(tx.get("merchant", ""), user_salt)
        if ref:
            tx["contact_ref"] = ref

    expenses = [
        tx for tx in transactions
        if tx.get("tx_type") == "expense" and tx.get("contact_ref")
    ]
    incomes = [
        tx for tx in transactions
        if tx.get("tx_type") == "income" and tx.get("contact_ref")
    ]

    pairs: list[SettlementPair] = []
    used_income_ids: set[int] = set()

    for exp in expenses:
        exp_date = date.fromisoformat(exp["date"]) if isinstance(exp["date"], str) else exp["date"]
        for inc in incomes:
            if inc["id"] in used_income_ids:
                continue
            if inc.get("contact_ref") != exp.get("contact_ref"):
                continue
            inc_date = date.fromisoformat(inc["date"]) if isinstance(inc["date"], str) else inc["date"]
            if abs((inc_date - exp_date).days) <= 7:
                net = Decimal(str(inc["amount"])) - Decimal(str(exp["amount"]))
                pairs.append(
                    SettlementPair(
                        expense_tx_id=exp["id"],
                        income_tx_id=inc["id"],
                        contact_ref=exp["contact_ref"],
                        net_amount=net,
                    )
                )
                used_income_ids.add(inc["id"])
                break

    return pairs
```
</document>

<document path="./src/services/dashboard_service.py">
```py
"""
Dashboard service.
"""
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.account_repo import AccountRepository
from src.repositories.transaction_repo import TransactionRepository
from src.schemas.dashboard import (
    BalanceOverview,
    DashboardData,
    IncomeExpenseSummary,
)
from src.schemas.account import AccountResponse
from src.schemas.transaction import TransactionResponse


class DashboardService:
    """Service for dashboard data aggregation."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.account_repo = AccountRepository(session)
        self.transaction_repo = TransactionRepository(session)

    async def get_dashboard_data(
        self,
        user_id: int,
        period_start: date | None = None,
        period_end: date | None = None,
    ) -> DashboardData:
        """
        Get dashboard data for user.
        
        Args:
            user_id: User ID
            period_start: Start date (default: 30 days ago)
            period_end: End date (default: today)
            
        Returns:
            Dashboard data
        """
        # Default period: last 30 days
        if not period_end:
            period_end = date.today()
        
        if not period_start:
            period_start = period_end - timedelta(days=30)
        
        # Get balance overview
        balance = await self._get_balance_overview(user_id)
        
        # Get income/expense summary
        income_expense = await self._get_income_expense_summary(
            user_id, period_start, period_end
        )
        
        # Get top accounts
        accounts = await self.account_repo.get_user_accounts(
            user_id, include_inactive=False, limit=5
        )
        top_accounts = [AccountResponse.model_validate(acc) for acc in accounts]
        
        # Get recent transactions
        transactions = await self.transaction_repo.get_recent_transactions(
            user_id, limit=10
        )
        recent_transactions = [
            TransactionResponse.model_validate(tx) for tx in transactions
        ]
        
        return DashboardData(
            period_start=period_start,
            period_end=period_end,
            balance=balance,
            income_expense=income_expense,
            top_accounts=top_accounts,
            recent_transactions=recent_transactions,
            expense_by_category=[],  # TODO: Implement in analytics service
            income_by_category=[],   # TODO: Implement in analytics service
            monthly_trend=[],         # TODO: Implement in analytics service
        )

    async def _get_balance_overview(self, user_id: int) -> BalanceOverview:
        """Get balance overview."""
        total_balance = await self.account_repo.get_total_balance(user_id)
        
        accounts = await self.account_repo.get_user_accounts(
            user_id, include_inactive=False
        )
        
        return BalanceOverview(
            total_balance=total_balance,
            currency="RUB",
            change_amount=Decimal("0.00"),  # TODO: Calculate from previous period
            change_percentage=0.0,
            account_count=len(accounts),
        )

    async def _get_income_expense_summary(
        self, user_id: int, date_from: date, date_to: date
    ) -> IncomeExpenseSummary:
        """Get income/expense summary."""
        total_income = await self.transaction_repo.get_total_by_type(
            user_id, "income", date_from, date_to
        )
        
        total_expense = await self.transaction_repo.get_total_by_type(
            user_id, "expense", date_from, date_to
        )
        
        return IncomeExpenseSummary(
            total_income=total_income,
            total_expense=total_expense,
            net_amount=total_income - total_expense,
            income_count=0,  # TODO: Add count to repository
            expense_count=0,
        )

```
</document>

<document path="./src/services/rule_engine.py">
```py
"""Deterministic rule engine for transaction enrichment."""
from typing import Any, Callable

RuleAction = dict[str, Any]


def _merchant(tx: dict) -> str:
    return (tx.get("merchant") or "").upper()


def _merchant_low(tx: dict) -> str:
    return (tx.get("merchant") or "").lower()


RULES: list[dict] = [
    {
        "id": "T-01",
        "condition": lambda tx: any(
            p in _merchant(tx) for p in ["VKLAD-KARTA", "KARTA-VKLAD", "KOPILKA", "SBER-VKLAD"]
        ),
        "action": {
            "enriched_type": "internal_transfer",
            "enriched_category": "Внутренний перевод",
            "exclude_from_metrics": True,
            "income_type": "internal",
            "expense_type": "internal",
            "review_status": "auto",
        },
    },
    {
        "id": "T-02",
        "condition": lambda tx: (
            any(kw in _merchant_low(tx) for kw in ["заработная плата", "зарплата", "salary"])
            and tx.get("tx_type") == "income"
        ),
        "action": {
            "enriched_category": "Зарплата",
            "income_type": "operational",
            "exclude_from_metrics": False,
            "review_status": "auto",
        },
    },
    {
        "id": "T-03",
        "condition": lambda tx: any(
            p in _merchant(tx)
            for p in ["SPOTIFY", "NETFLIX", "APPSTORE", "GOOGLE*", "YANDEX*PLUS", "YANDEX*MUSIC", "OKKO"]
        ),
        "action": {
            "enriched_category": "Подписки",
            "expense_type": "subscription",
            "exclude_from_metrics": False,
            "review_status": "auto",
        },
    },
    {
        "id": "T-04",
        "condition": lambda tx: any(p in _merchant(tx) for p in ["YANDEX*GO", "YANDEXGO", "UBER", "CITYMOBIL"]),
        "action": {
            "enriched_category": "Такси",
            "expense_type": "oneoff",
            "exclude_from_metrics": False,
            "review_status": "auto",
        },
    },
    {
        "id": "T-05",
        "condition": lambda tx: "автоплатёж" in _merchant_low(tx) or "autoplatezh" in _merchant_low(tx),
        "action": {
            "enriched_category": "Обязательные платежи",
            "expense_type": "regular",
            "exclude_from_metrics": False,
            "review_status": "auto",
        },
    },
    {
        "id": "T-06",
        "condition": lambda tx: (
            any(kw in _merchant_low(tx) for kw in ["кэшбэк", "cashback", "cash back"])
            and tx.get("tx_type") == "income"
        ),
        "action": {
            "enriched_category": "Кэшбэк",
            "income_type": "return",
            "exclude_from_metrics": True,
            "review_status": "auto",
        },
    },
    {
        "id": "T-07",
        "condition": lambda tx: (
            any(kw in _merchant_low(tx) for kw in ["возврат", "refund", "return"])
            and tx.get("tx_type") == "income"
        ),
        "action": {
            "enriched_category": "Возврат",
            "income_type": "return",
            "exclude_from_metrics": False,
            "review_status": "auto",
        },
    },
]


def apply_rules(tx: dict) -> RuleAction | None:
    """Apply rules in priority order. Returns first matching action or None."""
    for rule in RULES:
        try:
            if rule["condition"](tx):
                return dict(rule["action"])
        except Exception:
            continue
    return None
```
</document>

<document path="./src/services/transaction_service.py">
```py
"""
Transaction service.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.repositories.account_repo import AccountRepository
from src.repositories.category_repo import CategoryRepository
from src.repositories.transaction_repo import TransactionRepository
from src.schemas.base import PaginatedResponse, PaginationParams
from src.schemas.transaction import (
    TransactionCreate,
    TransactionDetail,
    TransactionFilters,
    TransactionResponse,
    TransactionUpdate,
)


class TransactionService:
    """Service for transaction management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.transaction_repo = TransactionRepository(session)
        self.account_repo = AccountRepository(session)
        self.category_repo = CategoryRepository(session)

    async def create_transaction(
        self, user_id: int, data: TransactionCreate
    ) -> TransactionResponse:
        """
        Create new transaction with balance update.
        
        Args:
            user_id: User ID
            data: Transaction data
            
        Returns:
            Created transaction
            
        Raises:
            NotFoundError: If account/category not found
            AuthorizationError: If user doesn't own account
            ValidationError: If validation fails
        """
        # Verify account ownership
        account = await self.account_repo.get_by_id(data.account_id)
        if not account:
            raise NotFoundError("Account not found")
        
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this account")
        
        # Verify category if provided
        if data.category_id:
            category = await self.category_repo.get_by_id(data.category_id)
            if not category:
                raise NotFoundError("Category not found")
        
        # For transfers, verify target account
        if data.transaction_type == "transfer":
            if not data.target_account_id:
                raise ValidationError("Target account required for transfers")
            
            target_account = await self.account_repo.get_by_id(data.target_account_id)
            if not target_account:
                raise NotFoundError("Target account not found")
            
            if target_account.user_id != user_id:
                raise AuthorizationError("Access denied to target account")
            
            if data.account_id == data.target_account_id:
                raise ValidationError("Cannot transfer to the same account")
        
        # Create transaction
        transaction = await self.transaction_repo.create(
            user_id=user_id,
            account_id=data.account_id,
            category_id=data.category_id,
            transaction_date=data.transaction_date,
            amount=data.amount,
            transaction_type=data.transaction_type,
            description=data.description,
            notes=data.notes,
            merchant=data.merchant,
            location=data.location,
            tags=data.tags,
            target_account_id=data.target_account_id,
        )
        
        # Update account balance
        await self._update_balance_for_transaction(
            account_id=data.account_id,
            amount=data.amount,
            transaction_type=data.transaction_type,
            target_account_id=data.target_account_id,
        )
        
        await self.session.commit()
        
        return TransactionResponse.model_validate(transaction)

    async def get_transaction(
        self, transaction_id: int, user_id: int
    ) -> TransactionDetail:
        """
        Get transaction by ID with relationships.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            
        Returns:
            Transaction with details
            
        Raises:
            NotFoundError: If transaction not found
            AuthorizationError: If user doesn't own transaction
        """
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        
        if not transaction:
            raise NotFoundError("Transaction not found")
        
        # Check ownership through account
        account = await self.account_repo.get_by_id(transaction.account_id)
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this transaction")
            
        # ПРИСВАИВАЕМ связи вручную (Fix бага валидации):
        transaction.account = account
        if transaction.category_id:
            # Импортируем репозиторий, если его еще нет в __init__
            from src.repositories.category_repo import CategoryRepository
            category_repo = CategoryRepository(self.session)
            transaction.category = await category_repo.get_by_id(transaction.category_id)
        else:
            transaction.category = None
            
        return TransactionDetail.model_validate(transaction)


    async def get_user_transactions(
        self,
        user_id: int,
        filters: TransactionFilters,
        pagination: PaginationParams,
    ) -> PaginatedResponse:
        # Получаем total отдельным COUNT-запросом
        total = await self.transaction_repo.count_user_transactions(
            user_id=user_id,
            account_id=filters.account_id,
            category_id=filters.category_id,
            transaction_type=filters.transaction_type,
            date_from=filters.date_from,
            date_to=filters.date_to,
            search=filters.search,
        )

        transactions = await self.transaction_repo.get_user_transactions(
            user_id=user_id,
            account_id=filters.account_id,
            category_id=filters.category_id,
            transaction_type=filters.transaction_type,
            date_from=filters.date_from,
            date_to=filters.date_to,
            search=filters.search,
            skip=pagination.offset,
            limit=pagination.limit,
        )

        items = [TransactionResponse.model_validate(tx) for tx in transactions]
        return PaginatedResponse.create(
            items=items,
            total=total,           # ← теперь реальный total
            page=pagination.page,
            page_size=pagination.page_size,
        )


    async def update_transaction(
        self, transaction_id: int, user_id: int, data: TransactionUpdate
    ) -> TransactionResponse:
        """
        Update transaction.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            data: Update data
            
        Returns:
            Updated transaction
            
        Raises:
            NotFoundError: If transaction not found
            AuthorizationError: If user doesn't own transaction
        """
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        
        if not transaction:
            raise NotFoundError("Transaction not found")
        
        account = await self.account_repo.get_by_id(transaction.account_id)
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this transaction")
        
        # Revert old balance changes
        await self._revert_balance_for_transaction(transaction)
        
        # Update transaction
        updated = await self.transaction_repo.update(
            transaction_id,
            **data.model_dump(exclude_unset=True),
        )
        
        # Apply new balance changes
        await self._update_balance_for_transaction(
            account_id=updated.account_id,
            amount=updated.amount,
            transaction_type=updated.transaction_type,
            target_account_id=updated.target_account_id,
        )
        
        await self.session.commit()
        
        return TransactionResponse.model_validate(updated)

    async def delete_transaction(
        self, transaction_id: int, user_id: int
    ) -> bool:
        """
        Delete transaction and revert balance.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundError: If transaction not found
            AuthorizationError: If user doesn't own transaction
        """
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        
        if not transaction:
            raise NotFoundError("Transaction not found")
        
        account = await self.account_repo.get_by_id(transaction.account_id)
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this transaction")
        
        # Revert balance changes
        await self._revert_balance_for_transaction(transaction)
        
        # Delete transaction
        deleted = await self.transaction_repo.delete(transaction_id)
        
        await self.session.commit()
        
        return deleted

    async def _update_balance_for_transaction(
        self,
        account_id: int,
        amount: Decimal,
        transaction_type: str,
        target_account_id: int | None = None,
    ) -> None:
        """Update account balance based on transaction."""
        if transaction_type == "income":
            await self.account_repo.update_balance(account_id, amount, "add")
        
        elif transaction_type == "expense":
            await self.account_repo.update_balance(account_id, amount, "subtract")
        
        elif transaction_type == "transfer" and target_account_id:
            # Subtract from source
            await self.account_repo.update_balance(account_id, amount, "subtract")
            # Add to target
            await self.account_repo.update_balance(target_account_id, amount, "add")

    async def _revert_balance_for_transaction(self, transaction) -> None:
        """Revert balance changes from transaction."""
        if transaction.transaction_type == "income":
            await self.account_repo.update_balance(
                transaction.account_id, transaction.amount, "subtract"
            )
        
        elif transaction.transaction_type == "expense":
            await self.account_repo.update_balance(
                transaction.account_id, transaction.amount, "add"
            )
        
        elif transaction.transaction_type == "transfer" and transaction.target_account_id:
            # Reverse: add to source
            await self.account_repo.update_balance(
                transaction.account_id, transaction.amount, "add"
            )
            # Subtract from target
            await self.account_repo.update_balance(
                transaction.target_account_id, transaction.amount, "subtract"
            )

```
</document>

<document path="./src/services/notify_listener_service.py">
```py
"""
PostgreSQL LISTEN воркер — слушает канал new_finance_transaction.
"""
import asyncio
import json
import logging

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.config import settings

logger = logging.getLogger(__name__)

# Создаём собственную фабрику сессий для воркера
# (не зависит от FastAPI dependency injection)
_engine = create_async_engine(settings.DATABASE_URL, echo=False)
_session_factory = async_sessionmaker(
    _engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def listen_for_transactions() -> None:
    conn = await asyncpg.connect(
        settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    )
    logger.info("LISTEN new_finance_transaction — воркер запущен")

    async def handle(connection, pid, channel, payload):
        try:
            data        = json.loads(payload)
            telegram_id = data.get("telegram_id")
            if not telegram_id:
                logger.warning("NOTIFY получен без telegram_id")
                return

            logger.info(f"NOTIFY получен: telegram_id={telegram_id}")

            # Импортируем здесь чтобы избежать circular imports
            from src.services.import_service import ImportService

            async with _session_factory() as session:
                service = ImportService(session)
                count   = await service.process_pending(int(telegram_id))
                logger.info(
                    f"Импорт завершён: {count} транзакций для telegram_id={telegram_id}"
                )

        except Exception as e:
            logger.exception(f"Ошибка в handle_notify: {e}")
            # logger.exception — выведет полный traceback, а не только сообщение

    await conn.add_listener("new_finance_transaction", handle)

    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await conn.remove_listener("new_finance_transaction", handle)
        await conn.close()
        await _engine.dispose()

```
</document>

<document path="./src/services/auth_service.py">
```py
"""
Authentication service.
"""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from src.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from src.models.user import User
from src.repositories.category_repo import CategoryRepository
from src.repositories.user_repo import UserRepository
from src.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, Token
from src.schemas.user import UserResponse


class AuthService:
    """Service for authentication and authorization."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.category_repo = CategoryRepository(session)

    async def register(self, data: RegisterRequest) -> AuthResponse:
        """
        Register new user.
        
        Args:
            data: Registration data
            
        Returns:
            Auth response with user and tokens
            
        Raises:
            ConflictError: If email or username already exists
        """
        # Check if email exists
        if await self.user_repo.email_exists(data.email):
            raise ConflictError(f"Email {data.email} already registered")
        
        # Check if username exists
        if await self.user_repo.username_exists(data.username):
            raise ConflictError(f"Username {data.username} already taken")
        
        # Create user
        hashed_password = get_password_hash(data.password)
        user = await self.user_repo.create(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        
        # Create default categories for new user
        await self.category_repo.create_default_categories(user.id)
        await self.session.commit()
        
        # Generate tokens
        tokens = self._create_tokens(user.id)
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def login(self, data: LoginRequest) -> AuthResponse:
        """
        Login user by email or username.
        """
        # Определяем тип по наличию @ — валидатор уже проверил формат
        if "@" in data.login:
            user = await self.user_repo.get_by_email(data.login)
        else:
            user = await self.user_repo.get_by_username(data.login)

        # Единое сообщение — не раскрываем что именно не так
        if not user or not verify_password(data.password, user.hashed_password):
            raise AuthenticationError("Invalid email/username or password")

        if not user.is_active:
            raise AuthenticationError("User account is disabled")

        tokens = self._create_tokens(user.id)

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )
    
    async def refresh_token(self, refresh_token: str) -> Token:
        """
        Refresh access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token pair
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if not user_id or token_type != "refresh":
                raise AuthenticationError("Invalid refresh token")
            
            # Check if user exists and is active
            user = await self.user_repo.get_by_id(int(user_id))
            if not user or not user.is_active:
                raise AuthenticationError("User not found or disabled")
            
            # Generate new tokens
            return self._create_tokens(user.id)
            
        except JWTError:
            raise AuthenticationError("Invalid refresh token")

    async def get_current_user(self, token: str) -> User:
        """
        Get current user from access token.
        
        Args:
            token: Access token
            
        Returns:
            Current user
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if not user_id or token_type != "access":
                raise AuthenticationError("Invalid access token")
            
            user = await self.user_repo.get_by_id(int(user_id))
            
            if not user:
                raise NotFoundError("User not found")
            
            if not user.is_active:
                raise AuthenticationError("User account is disabled")
            
            return user
            
        except JWTError:
            raise AuthenticationError("Invalid access token")

    async def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful
            
        Raises:
            AuthenticationError: If old password is wrong
            NotFoundError: If user not found
        """
        user = await self.user_repo.get_by_id(user_id)
        
        if not user:
            raise NotFoundError("User not found")
        
        # Verify old password
        if not verify_password(old_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect")
        
        # Update password
        hashed_password = get_password_hash(new_password)
        await self.user_repo.update(user_id, hashed_password=hashed_password)
        
        return True

    def _create_tokens(self, user_id: int) -> Token:
        """Create access and refresh tokens."""
        access_token = create_access_token(str(user_id))
        refresh_token = create_refresh_token(str(user_id))
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

```
</document>

<document path="./src/services/account_service.py">
```py
"""
Account service.
"""
"""
Account service.
"""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.repositories.account_repo import AccountRepository
from src.schemas.account import (
    AUTO_IMPORT_TYPES,
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    AccountWithStats,
)


class AccountService:
    """Service for account management."""

    def __init__(self, session: AsyncSession):
        self.session      = session
        self.account_repo = AccountRepository(session)

    # ------------------------------------------------------------------ #
    # Create                                                               #
    # ------------------------------------------------------------------ #

    async def create_account(
        self, user_id: int, data: AccountCreate
    ) -> AccountResponse:
        """Создать счёт (только cash через API)."""
        account = await self.account_repo.create(
            user_id          = user_id,
            name             = data.name,
            account_type     = data.account_type,
            currency         = data.currency,
            balance          = data.balance,
            bank_name        = data.bank_name,
            last_four_digits = data.last_four_digits,
            icon             = data.icon,
            color            = data.color,
            include_in_total = data.include_in_total,
            is_active        = True,
        )
        return AccountResponse.model_validate(account)

    async def create_account_from_import(
        self,
        user_id:          int,
        name:             str,
        account_type:     str,          # "card" | "bank_account"
        currency:         str,
        balance:          Decimal,
        bank_name:        str | None    = None,
        last_four_digits: str | None    = None,
        account_number:   str | None    = None,
    ) -> AccountResponse:
        """
        Создать банковский счёт/карту через ImportService.
        Минует валидатор AccountCreate.only_cash_allowed.
        """
        account = await self.account_repo.create(
            user_id          = user_id,
            name             = name,
            account_type     = account_type,
            currency         = currency,
            balance          = balance,
            bank_name        = bank_name,
            last_four_digits = last_four_digits,
            account_number   = account_number,
            include_in_total = True,
            is_active        = True,
        )
        return AccountResponse.model_validate(account)

    # ------------------------------------------------------------------ #
    # Read                                                                 #
    # ------------------------------------------------------------------ #

    async def get_account(self, account_id: int, user_id: int) -> AccountResponse:
        account = await self.account_repo.get_by_id(account_id)

        if not account:
            raise NotFoundError("Account not found")
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this account")

        return AccountResponse.model_validate(account)

    async def get_user_accounts(
        self, user_id: int, include_inactive: bool = False
    ) -> list[AccountResponse]:
        accounts = await self.account_repo.get_user_accounts(
            user_id          = user_id,
            include_inactive = include_inactive,
        )
        return [AccountResponse.model_validate(acc) for acc in accounts]

    async def get_accounts_by_type(
        self, user_id: int, account_type: str
    ) -> list[AccountResponse]:
        accounts = await self.account_repo.get_by_type(user_id, account_type)
        return [AccountResponse.model_validate(acc) for acc in accounts]

    async def get_total_balance(
        self, user_id: int, currency: str = "RUB"
    ) -> Decimal:
        return await self.account_repo.get_total_balance(user_id, currency)
    
    async def get_balances_by_currency(self, user_id: int) -> dict[str, Decimal]:
        return await self.account_repo.get_balances_by_currency(user_id)

    # ------------------------------------------------------------------ #
    # Update                                                               #
    # ------------------------------------------------------------------ #

    async def update_account(
        self, account_id: int, user_id: int, data: AccountUpdate
    ) -> AccountResponse:
        """
        Обновить счёт с проверкой бизнес-правил.

        Правила:
        - cash → нельзя менять тип, нельзя менять bank_name
        - card/bank_account → можно менять тип только card ↔ bank_account
        - нельзя переключить банковский счёт в cash
        """
        account = await self.account_repo.get_by_id(account_id)

        if not account:
            raise NotFoundError("Account not found")
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this account")

        update_data = data.model_dump(exclude_unset=True)
        if 'balance' in update_data and account.account_type != 'cash':
            del update_data['balance']
        # --- Проверка изменения типа ---
        new_type = update_data.get("account_type")
        if new_type is not None:
            current_type = account.account_type

            if current_type == "cash":
                raise ValidationError(
                    "Нельзя изменить тип счёта наличных. "
                    "Удалите его и дождитесь автоимпорта из выписки."
                )
            if new_type == "cash":
                raise ValidationError(
                    "Нельзя изменить банковский счёт на наличные."
                )
            # Разрешено только card ↔ bank_account — проходит без ошибки

        # --- Запрет bank_name для наличных ---
        if account.account_type == "cash" and "bank_name" in update_data:
            del update_data["bank_name"]

        # --- Страховка: убираем поля, которых нет в AccountUpdate ---
        # (на случай если repo.update принимает **kwargs)
        FORBIDDEN = {"last_four_digits", "account_number", "user_id"}
        for field in FORBIDDEN:
            update_data.pop(field, None)

        if not update_data:
            return AccountResponse.model_validate(account)

        updated = await self.account_repo.update(account_id, **update_data)
        return AccountResponse.model_validate(updated)

    # ------------------------------------------------------------------ #
    # Delete                                                             #
    # ------------------------------------------------------------------ #

    async def delete_account(self, account_id: int, user_id: int) -> bool:
        """
        Удалить счёт.
        Банковские счета/карты с транзакциями — только деактивация (soft delete).
        Наличные — полное удаление.
        """
        account = await self.account_repo.get_by_id(account_id)

        if not account:
            raise NotFoundError("Account not found")
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this account")

        if account.account_type in AUTO_IMPORT_TYPES:
            # Мягкое удаление — просто деактивируем
            await self.account_repo.update(account_id, is_active=False)
            return True

        # Для наличных — полное удаление
        return await self.account_repo.delete(account_id)

    # ------------------------------------------------------------------ #
    # Import Service                                                     #
    # ------------------------------------------------------------------ #
    
    async def get_accounts_by_number(
        self, user_id: int, account_number: str
    ) -> AccountResponse | None:
        """Поиск счёта по полному номеру."""
        result = await self.account_repo.get_by_account_number(user_id, account_number)
        return AccountResponse.model_validate(result) if result else None

    async def get_account_by_last4(
        self, user_id: int, last4: str
    ) -> AccountResponse | None:
        """Поиск карты/счёта по последним 4 цифрам."""
        result = await self.account_repo.get_by_last_four(user_id, last4)
        return AccountResponse.model_validate(result) if result else None

    async def update_account_number(
        self, account_id: int, account_number: str
    ) -> None:
        """Обновить полный номер счёта (только для ImportService)."""
        await self.account_repo.update(account_id, account_number=account_number)
```
</document>

<document path="./src/services/telegram_service.py">
```py
"""Telegram service with atomic token consumption (SEC-01, SEC-10)."""
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.telegram_link_token import TelegramLinkToken
from src.config import settings


class TelegramService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def generate_link_token(self, user_id: int) -> TelegramLinkToken:
        """Generate a new Telegram link token (invalidates old ones)."""
        old_tokens = await self.session.execute(
            select(TelegramLinkToken).where(
                TelegramLinkToken.user_id == user_id,
                TelegramLinkToken.used == False,  # noqa: E712
            )
        )
        for token in old_tokens.scalars().all():
            token.used = True
            self.session.add(token)

        token = TelegramLinkToken(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            used=False,
        )
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def link_telegram(
        self,
        raw_token: str,
        telegram_id: int,
        telegram_username: str | None = None,
    ) -> User:
        """
        Atomically consume token and link Telegram (SEC-10).
        Uses UPDATE...WHERE used=FALSE RETURNING to prevent race conditions.
        """
        stmt = (
            update(TelegramLinkToken)
            .where(
                TelegramLinkToken.token == raw_token,
                TelegramLinkToken.used == False,  # noqa: E712
                TelegramLinkToken.expires_at > datetime.now(timezone.utc),
            )
            .values(used=True)
            .returning(TelegramLinkToken)
        )
        result = await self.session.execute(stmt)
        link_token = result.scalar_one_or_none()
        if not link_token:
            # Do NOT reveal whether token is invalid vs expired (SEC-01)
            raise ValueError("Invalid or expired token")

        # Check telegram_id not already linked to another user
        existing = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        existing_user = existing.scalar_one_or_none()
        if existing_user and existing_user.id != link_token.user_id:
            raise ValueError("Invalid or expired token")

        user_result = await self.session.execute(
            select(User).where(User.id == link_token.user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("Invalid or expired token")

        user.telegram_id = telegram_id
        user.telegram_username = telegram_username
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_status(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def unlink_telegram(self, user_id: int) -> None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.telegram_id = None
            user.telegram_username = None
            self.session.add(user)
            await self.session.commit()
```
</document>

<document path="./src/services/enrichment_service.py">
```py
"""Enrichment orchestrator — runs rule engine + LLM on transactions."""
import asyncio
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.transaction import Transaction
from src.services.llm_privacy import (
    LLM_SYSTEM_PROMPT,
    build_llm_prompt,
    prepare_batch_for_llm,
)
from src.services.rule_engine import apply_rules

logger = logging.getLogger(__name__)

BATCH_SIZE = 20
MAX_RETRIES = 3


async def _call_llm_with_retry(prompt: str) -> dict | None:
    """Call LLM API with exponential backoff. Returns parsed JSON or None."""
    for attempt in range(MAX_RETRIES):
        try:
            if settings.LLM_PROVIDER == "openai":
                result = await _call_openai(prompt)
            elif settings.LLM_PROVIDER == "anthropic":
                result = await _call_anthropic(prompt)
            else:
                return None
            return result
        except Exception as exc:
            wait = 2 ** attempt
            logger.warning("LLM call failed attempt=%d error=%s retry_in=%ds", attempt + 1, type(exc).__name__, wait)
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(wait)
    return None


async def _call_openai(prompt: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": LLM_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
            },
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)


async def _call_anthropic(prompt: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 512,
                "system": LLM_SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        content = resp.json()["content"][0]["text"]
        return json.loads(content)


async def _get_user_salt(session: AsyncSession, telegram_id: int) -> bytes:
    """Fetch user_salt from user_keys table."""
    from sqlalchemy import text
    result = await session.execute(
        text("SELECT salt FROM finances.user_keys WHERE telegram_id = :tid"),
        {"tid": telegram_id},
    )
    row = result.fetchone()
    if row:
        return bytes.fromhex(row[0]) if isinstance(row[0], str) else row[0]
    # Fallback: derive from secret key (should not happen in production)
    import hmac, hashlib
    return hmac.new(settings.SECRET_KEY.encode(), str(telegram_id).encode(), hashlib.sha256).digest()


async def enrich_transactions(
    session: AsyncSession,
    transactions: list[Transaction],
    telegram_id: int,
) -> None:
    """
    Main enrichment pipeline:
    1. Apply deterministic rule engine
    2. Send unresolved transactions to LLM (batched, privacy-sanitized)
    3. Write enrichment fields back to DB
    """
    if not transactions:
        return

    user_salt = await _get_user_salt(session, telegram_id)

    # Phase 1: Rule engine
    rule_resolved: list[Transaction] = []
    llm_pending: list[Transaction] = []

    for tx in transactions:
        tx_dict = _tx_to_dict(tx)
        rule_result = apply_rules(tx_dict)
        
        if settings.PIPELINE_LOG_VERBOSE:
            logger.info(
                f"[RULE ENGINE] tx_id={tx.id} merchant='{tx.merchant}' "
                f"→ {'MATCH: ' + str(rule_result) if rule_result else 'no match'}"
            )

        if rule_result:
            await _apply_enrichment(session, tx.id, rule_result, source="rule", confidence=Decimal("1.00"))
            rule_resolved.append(tx)
        else:
            llm_pending.append(tx)

    if settings.PIPELINE_LOG_VERBOSE:
        logger.info(f"[PIPELINE] Rule resolved: {len(rule_resolved)}, LLM pending: {len(llm_pending)}")

    # Phase 2: LLM batch
    if not settings.PIPELINE_LLM or not llm_pending:
        if settings.PIPELINE_LOG_VERBOSE and llm_pending:
            logger.info(f"[PIPELINE] LLM disabled, {len(llm_pending)} transactions left unenriched")
        await session.commit()
        return


    for i in range(0, len(llm_pending), BATCH_SIZE):
        batch = llm_pending[i : i + BATCH_SIZE]
        batch_dicts = [_tx_to_dict(tx) for tx in batch]
        sanitized_batch, _ = prepare_batch_for_llm(batch_dicts, user_salt)

        tasks = [_call_llm_with_retry(build_llm_prompt(s)) for s in sanitized_batch]
        results = await asyncio.gather(*tasks)

        for tx, llm_result in zip(batch, results):
            if llm_result:
                confidence = Decimal(str(llm_result.get("confidence", 0.5)))
                review_status = "pending" if llm_result.get("needs_user_review") else "auto"
                enrichment = {
                    "enriched_category": llm_result.get("enriched_category"),
                    "income_type": llm_result.get("income_type"),
                    "expense_type": llm_result.get("expense_type"),
                    "exclude_from_metrics": llm_result.get("exclude_from_metrics", False),
                    "is_group_payment": llm_result.get("is_group_payment_suspect", False),
                    "review_status": review_status,
                }
                # Log only id + confidence — NEVER merchant
                logger.info("enriched transaction_id=%d confidence=%s", tx.id, confidence)
                await _apply_enrichment(session, tx.id, enrichment, source="llm", confidence=confidence)

    await session.commit()


async def _apply_enrichment(
    session: AsyncSession,
    tx_id: int,
    enrichment: dict,
    source: str,
    confidence: Decimal,
) -> None:
    enrichment["enrichment_source"] = source
    enrichment["enrichment_confidence"] = confidence
    enrichment["enriched_at"] = datetime.now(timezone.utc)
    await session.execute(
        update(Transaction).where(Transaction.id == tx_id).values(**enrichment)
    )


def _tx_to_dict(tx: Transaction) -> dict:
    return {
        "id": tx.id,
        "date": str(tx.transaction_date),
        "amount": float(tx.amount),
        "tx_type": tx.transaction_type,
        "bank_category": tx.description or "",
        "merchant": tx.merchant or "",
        "balance": 0,  # balance not stored per-tx in current schema
    }
```
</document>

<document path="./src/services/__init__.py">
```py
"""
Business logic layer - Services.
"""
from src.services.account_service import AccountService
from src.services.auth_service import AuthService
from src.services.category_service import CategoryService
from src.services.dashboard_service import DashboardService
from src.services.transaction_service import TransactionService

__all__ = [
    "AuthService",
    "AccountService",
    "CategoryService",
    "TransactionService",
    "DashboardService",
]

```
</document>

<document path="./alembic/README">
```/alembic/README
Generic single-database configuration with an async dbapi.```
</document>

<document path="./alembic/script.py.mako">
```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```
</document>

<document path="./alembic/env.py">
```py
# alembic/env.py
from __future__ import annotations
import asyncio  # ← отсутствует
from logging.config import fileConfig  # ← отсутствует

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.engine import Connection

from src.config import settings
from src.models.base import Base
from src.models.user import User
from src.models.account import Account
from src.models.category import Category
from src.models.transaction import Transaction
from src.models.budget import Budget
from src.models.telegram_link_token import TelegramLinkToken  # ← добавить после создания модели

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Указываем обе схемы
target_metadata.schema_translate_map = None


def get_url() -> str:
    return settings.DATABASE_URL

MANAGED_SCHEMAS = {"finances", "public"}


def include_object(object, name, type_, reflected, compare_to):
    """
    Говорим Alembic какие объекты включать в миграции.
    Всё что не в MANAGED_SCHEMAS — игнорируем.
    """
    # Для таблиц проверяем схему
    if type_ == "table":
        schema = object.schema if hasattr(object, "schema") else None
        if schema not in MANAGED_SCHEMAS:
            return False  # ← не трогаем bot, public и т.д.

    # Для индексов и остального — берём схему из таблицы
    if type_ in ("index", "unique_constraint", "foreign_key_constraint"):
        table_schema = getattr(object.table, "schema", None)
        if table_schema not in MANAGED_SCHEMAS:
            return False

    return True

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_async_migrations())

run_migrations()

```
</document>

<document path="./alembic/versions/3e9329094e83_add_streak_to_habits.py">
```py
"""add streak to habits

Revision ID: 3e9329094e83
Revises: 8aae31dde3c6
Create Date: 2026-03-26 20:43:46.147532+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e9329094e83'
down_revision: Union[str, None] = '8aae31dde3c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'accounts', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'categories', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'habit_logs', 'habits', ['habit_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.add_column('habits', sa.Column('current_streak', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'habits', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'telegram_link_tokens', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'accounts', ['account_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'accounts', ['target_account_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='SET NULL')
    op.create_foreign_key(None, 'transactions', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='SET NULL')
    op.create_foreign_key(None, 'transactions', 'transactions', ['linked_tx_id'], ['id'], source_schema='finances', referent_schema='finances')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'telegram_link_tokens', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'habits', schema='finances', type_='foreignkey')
    op.drop_column('habits', 'current_streak')
    op.drop_constraint(None, 'habit_logs', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'categories', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'accounts', schema='finances', type_='foreignkey')
    # ### end Alembic commands ###
```
</document>

<document path="./alembic/versions/001_initial_schema.py">
```py
"""initial_schema

Revision ID: 674e8f596e01
Revises: 4cae4220fc21
Create Date: 2026-03-23 13:48:45.967071+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'accounts', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'categories', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'telegram_link_tokens', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.add_column('transactions', sa.Column('enriched_category', sa.String(length=100), nullable=True))
    op.add_column('transactions', sa.Column('enriched_subcategory', sa.String(length=100), nullable=True))
    op.add_column('transactions', sa.Column('enriched_type', sa.String(length=50), nullable=True))
    op.add_column('transactions', sa.Column('income_type', sa.String(length=50), nullable=True))
    op.add_column('transactions', sa.Column('expense_type', sa.String(length=50), nullable=True))
    op.add_column('transactions', sa.Column('exclude_from_metrics', sa.Boolean(), nullable=False))
    op.add_column('transactions', sa.Column('is_group_payment', sa.Boolean(), nullable=False))
    op.add_column('transactions', sa.Column('net_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('transactions', sa.Column('linked_tx_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('enrichment_source', sa.String(length=20), nullable=True))
    op.add_column('transactions', sa.Column('enrichment_confidence', sa.Numeric(precision=3, scale=2), nullable=True))
    op.add_column('transactions', sa.Column('review_status', sa.String(length=20), nullable=False))
    op.add_column('transactions', sa.Column('user_rule_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('enriched_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('transactions', sa.Column('contact_ref', sa.String(length=24), nullable=True))
    op.alter_column('transactions', 'import_source',
               existing_type=sa.VARCHAR(length=20),
               server_default='manual',
               existing_nullable=False)
    op.create_index('idx_transactions_contact_ref', 'transactions', ['contact_ref'], unique=False, schema='finances')
    op.create_index('idx_transactions_review_status', 'transactions', ['review_status'], unique=False, schema='finances')
    op.create_index(op.f('ix_finances_transactions_contact_ref'), 'transactions', ['contact_ref'], unique=False, schema='finances')
    op.create_index(op.f('ix_finances_transactions_external_id'), 'transactions', ['external_id'], unique=True, schema='finances')
    op.create_index(op.f('ix_finances_transactions_id'), 'transactions', ['id'], unique=False, schema='finances')
    op.create_foreign_key(None, 'transactions', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='SET NULL')
    op.create_foreign_key(None, 'transactions', 'accounts', ['account_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'transactions', ['linked_tx_id'], ['id'], source_schema='finances', referent_schema='finances')
    op.create_foreign_key(None, 'transactions', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'accounts', ['target_account_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_index(op.f('ix_finances_transactions_id'), table_name='transactions', schema='finances')
    op.drop_index(op.f('ix_finances_transactions_external_id'), table_name='transactions', schema='finances')
    op.drop_index(op.f('ix_finances_transactions_contact_ref'), table_name='transactions', schema='finances')
    op.drop_index('idx_transactions_review_status', table_name='transactions', schema='finances')
    op.drop_index('idx_transactions_contact_ref', table_name='transactions', schema='finances')
    op.alter_column('transactions', 'import_source',
               existing_type=sa.VARCHAR(length=20),
               server_default=None,
               existing_nullable=False)
    op.drop_column('transactions', 'contact_ref')
    op.drop_column('transactions', 'enriched_at')
    op.drop_column('transactions', 'user_rule_id')
    op.drop_column('transactions', 'review_status')
    op.drop_column('transactions', 'enrichment_confidence')
    op.drop_column('transactions', 'enrichment_source')
    op.drop_column('transactions', 'linked_tx_id')
    op.drop_column('transactions', 'net_amount')
    op.drop_column('transactions', 'is_group_payment')
    op.drop_column('transactions', 'exclude_from_metrics')
    op.drop_column('transactions', 'expense_type')
    op.drop_column('transactions', 'income_type')
    op.drop_column('transactions', 'enriched_type')
    op.drop_column('transactions', 'enriched_subcategory')
    op.drop_column('transactions', 'enriched_category')
    op.drop_constraint(None, 'telegram_link_tokens', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'categories', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'accounts', schema='finances', type_='foreignkey')
    # ### end Alembic commands ###
```
</document>

<document path="./alembic/versions/0ac212ee8ce1_initial_schema.py">
```py
"""initial schema

Revision ID: 0ac212ee8ce1
Revises: 
Create Date: 2026-03-10 00:54:10.590722+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ac212ee8ce1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='finances'
    )
    op.create_index(op.f('ix_finances_users_email'), 'users', ['email'], unique=True, schema='finances')
    op.create_index(op.f('ix_finances_users_username'), 'users', ['username'], unique=True, schema='finances')
    op.create_table('accounts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('account_number', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('bank_name', sa.String(length=100), nullable=True),
    sa.Column('currency', sa.String(length=10), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='raw_operations'
    )
    op.create_table('finance_transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_number', sa.String(length=50), nullable=False),
    sa.Column('date_msk', sa.Date(), nullable=False),
    sa.Column('time_msk', sa.Time(), nullable=False),
    sa.Column('auth_code', sa.String(length=50), nullable=True),
    sa.Column('category', sa.String(length=255), nullable=True),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('tx_type', sa.String(length=20), nullable=True),
    sa.Column('balance', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('date_operation', sa.Date(), nullable=True),
    sa.Column('merchant', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='raw_operations'
    )
    op.create_table('users',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('telegram_id', sa.BigInteger(), nullable=True),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='raw_operations'
    )
    op.create_table('accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('account_type', sa.String(length=50), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('balance', sa.DECIMAL(precision=15, scale=2), nullable=False),
    sa.Column('bank_name', sa.String(length=100), nullable=True),
    sa.Column('account_number', sa.String(length=50), nullable=True),
    sa.Column('last_four_digits', sa.String(length=4), nullable=True),
    sa.Column('icon', sa.String(length=50), nullable=True),
    sa.Column('color', sa.String(length=7), nullable=True),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('include_in_total', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.CheckConstraint("account_type IN ('card', 'bank_account', 'cash', 'investment', 'crypto', 'other')", name='check_account_type'),
    sa.CheckConstraint('balance >= 0', name='check_balance_positive'),
    sa.ForeignKeyConstraint(['user_id'], ['finances.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='finances'
    )
    op.create_index('idx_accounts_type', 'accounts', ['account_type'], unique=False, schema='finances')
    op.create_index('idx_accounts_user', 'accounts', ['user_id'], unique=False, schema='finances')
    op.create_index(op.f('ix_finances_accounts_id'), 'accounts', ['id'], unique=False, schema='finances')
    op.create_table('categories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True, comment='NULL for system categories'),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('category_type', sa.String(length=20), nullable=False, comment='income, expense, transfer'),
    sa.Column('icon', sa.String(length=50), nullable=True),
    sa.Column('color', sa.String(length=7), nullable=True),
    sa.Column('is_system', sa.Boolean(), nullable=False, comment='System category (cannot be deleted by user)'),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['finances.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='finances'
    )
    op.create_index(op.f('ix_finances_categories_user_id'), 'categories', ['user_id'], unique=False, schema='finances')
    op.create_table('budgets',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True, comment='NULL for total budget'),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('period_type', sa.String(length=20), nullable=False, comment='daily, weekly, monthly, yearly'),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['finances.categories.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['finances.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='finances'
    )
    op.create_index(op.f('ix_finances_budgets_category_id'), 'budgets', ['category_id'], unique=False, schema='finances')
    op.create_index(op.f('ix_finances_budgets_user_id'), 'budgets', ['user_id'], unique=False, schema='finances')
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('target_account_id', sa.Integer(), nullable=True),
    sa.Column('transaction_date', sa.Date(), nullable=False),
    sa.Column('amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
    sa.Column('transaction_type', sa.String(length=20), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('merchant', sa.String(length=255), nullable=True),
    sa.Column('location', sa.String(length=255), nullable=True),
    sa.Column('tags', sa.String(length=500), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('receipt_url', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.CheckConstraint("transaction_type IN ('income', 'expense', 'transfer')", name='check_transaction_type'),
    sa.CheckConstraint('amount >= 0', name='check_amount_positive'),
    sa.ForeignKeyConstraint(['account_id'], ['finances.accounts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['category_id'], ['finances.categories.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['target_account_id'], ['finances.accounts.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['finances.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_transactions_account', 'transactions', ['account_id'], unique=False)
    op.create_index('idx_transactions_category', 'transactions', ['category_id'], unique=False)
    op.create_index('idx_transactions_type', 'transactions', ['transaction_type'], unique=False)
    op.create_index('idx_transactions_user_date', 'transactions', ['user_id', 'transaction_date'], unique=False)
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_index('idx_transactions_user_date', table_name='transactions')
    op.drop_index('idx_transactions_type', table_name='transactions')
    op.drop_index('idx_transactions_category', table_name='transactions')
    op.drop_index('idx_transactions_account', table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_finances_budgets_user_id'), table_name='budgets', schema='finances')
    op.drop_index(op.f('ix_finances_budgets_category_id'), table_name='budgets', schema='finances')
    op.drop_table('budgets', schema='finances')
    op.drop_index(op.f('ix_finances_categories_user_id'), table_name='categories', schema='finances')
    op.drop_table('categories', schema='finances')
    op.drop_index(op.f('ix_finances_accounts_id'), table_name='accounts', schema='finances')
    op.drop_index('idx_accounts_user', table_name='accounts', schema='finances')
    op.drop_index('idx_accounts_type', table_name='accounts', schema='finances')
    op.drop_table('accounts', schema='finances')
    op.drop_table('users', schema='raw_operations')
    op.drop_table('finance_transactions', schema='raw_operations')
    op.drop_table('accounts', schema='raw_operations')
    op.drop_index(op.f('ix_finances_users_username'), table_name='users', schema='finances')
    op.drop_index(op.f('ix_finances_users_email'), table_name='users', schema='finances')
    op.drop_table('users', schema='finances')
    # ### end Alembic commands ###
```
</document>

<document path="./alembic/versions/002_enrichment_fields.py">
```py
"""Add enrichment fields to transactions, contact_profiles, user_enrichment_rules, user_keys.

Revision ID: 002_enrichment
Revises: 001_initial
Create Date: 2026-03-23
"""
from alembic import op
import sqlalchemy as sa

revision = "002_enrichment"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enrichment columns on transactions
    op.add_column("transactions", sa.Column("enriched_category", sa.String(100), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("enriched_subcategory", sa.String(100), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("enriched_type", sa.String(50), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("income_type", sa.String(50), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("expense_type", sa.String(50), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("exclude_from_metrics", sa.Boolean(), nullable=False, server_default="false"), schema="finances")
    op.add_column("transactions", sa.Column("is_group_payment", sa.Boolean(), nullable=False, server_default="false"), schema="finances")
    op.add_column("transactions", sa.Column("net_amount", sa.Numeric(12, 2), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("linked_tx_id", sa.Integer(), sa.ForeignKey("finances.transactions.id"), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("enrichment_source", sa.String(20), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("enrichment_confidence", sa.Numeric(3, 2), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("review_status", sa.String(20), nullable=False, server_default="auto"), schema="finances")
    op.add_column("transactions", sa.Column("user_rule_id", sa.Integer(), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("enriched_at", sa.DateTime(timezone=True), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("contact_ref", sa.String(24), nullable=True), schema="finances")
    op.create_index("idx_transactions_review_status", "transactions", ["review_status"], schema="finances")
    op.create_index("idx_transactions_contact_ref", "transactions", ["contact_ref"], schema="finances")
    op.create_foreign_key(None, 'accounts', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'categories', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'telegram_link_tokens', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='SET NULL')
    op.create_foreign_key(None, 'transactions', 'accounts', ['account_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'accounts', ['target_account_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='SET NULL')
    op.create_index(op.f('ix_finances_transactions_external_id'), 'transactions', ['external_id'], unique=True, schema='finances')
    op.create_index(op.f('ix_finances_transactions_id'), 'transactions', ['id'], unique=False, schema='finances')

    # contact_profiles
    op.create_table(
        "contact_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("contact_ref", sa.String(24), nullable=False),
        sa.Column("relation_type", sa.String(30), nullable=False, server_default="unknown"),
        sa.Column("typical_amount_min", sa.Numeric(10, 2), nullable=True),
        sa.Column("typical_amount_max", sa.Numeric(10, 2), nullable=True),
        sa.Column("avg_frequency_days", sa.Integer(), nullable=True),
        sa.Column("last_seen_at", sa.Date(), nullable=True),
        sa.Column("tx_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("user_label", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("telegram_id", "contact_ref", name="uq_contact_per_user"),
        schema="finances",
    )

    # user_enrichment_rules
    op.create_table(
        "user_enrichment_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("rule_type", sa.String(50), nullable=False),
        sa.Column("match_pattern", sa.String(200), nullable=False),
        sa.Column("action_json", sa.JSON(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        schema="finances",
    )

    # user_keys — isolated salt storage
    op.create_table(
        "user_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True, index=True),
        sa.Column("salt", sa.String(64), nullable=False),  # hex-encoded 32-byte salt
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="finances",
    )


def downgrade() -> None:
    op.drop_table("user_keys", schema="finances")
    op.drop_table("user_enrichment_rules", schema="finances")
    op.drop_table("contact_profiles", schema="finances")
    op.drop_index("idx_transactions_contact_ref", "transactions", schema="finances")
    op.drop_index("idx_transactions_review_status", "transactions", schema="finances")
    for col in [
        "contact_ref", "enriched_at", "user_rule_id", "review_status",
        "enrichment_confidence", "enrichment_source", "linked_tx_id",
        "net_amount", "is_group_payment", "exclude_from_metrics",
        "expense_type", "income_type", "enriched_type",
        "enriched_subcategory", "enriched_category",
    ]:
        op.drop_column("transactions", col, schema="finances")
```
</document>

<document path="./alembic/versions/4cae4220fc21_add_external_id_import_source_to_.py">
```py
"""add_external_id_import_source_to_transactions

Revision ID: 4cae4220fc21
Revises: 5f93d75f9bcf
Create Date: 2026-03-18 14:28:21.049996+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cae4220fc21'
down_revision: Union[str, None] = '5f93d75f9bcf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'accounts', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'categories', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'telegram_link_tokens', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'telegram_link_tokens', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'categories', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'accounts', schema='finances', type_='foreignkey')
    # ### end Alembic commands ###
```
</document>

<document path="./alembic/versions/5f93d75f9bcf_change_telegram_id_to_bigint.py">
```py
"""change_telegram_id_to_bigint

Revision ID: 5f93d75f9bcf
Revises: 2a61cedac9c7
Create Date: 2026-03-18 12:24:35.187166+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5f93d75f9bcf'
down_revision: Union[str, None] = '2a61cedac9c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('telegram_upload_log', schema='bot')
    op.drop_index('ix_bot_ft_date_msk', table_name='finance_transactions', schema='bot')
    op.drop_index('ix_bot_ft_import_status', table_name='finance_transactions', schema='bot', postgresql_where="((import_status)::text = 'pending'::text)")
    op.drop_index('ix_bot_ft_telegram_id', table_name='finance_transactions', schema='bot')
    op.drop_index('ix_bot_ft_telegram_id_status', table_name='finance_transactions', schema='bot', postgresql_where="((import_status)::text = 'pending'::text)")
    op.drop_table('finance_transactions', schema='bot')
    op.drop_table('telegram_user_state', schema='bot')
    op.drop_constraint('accounts_user_id_fkey', 'accounts', type_='foreignkey')
    op.create_foreign_key(None, 'accounts', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.drop_constraint('budgets_category_id_fkey', 'budgets', type_='foreignkey')
    op.drop_constraint('budgets_user_id_fkey', 'budgets', type_='foreignkey')
    op.create_foreign_key(None, 'budgets', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.drop_constraint('categories_user_id_fkey', 'categories', type_='foreignkey')
    op.create_foreign_key(None, 'categories', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.drop_constraint('telegram_link_tokens_user_id_fkey', 'telegram_link_tokens', type_='foreignkey')
    op.create_foreign_key(None, 'telegram_link_tokens', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.drop_constraint('transactions_account_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('transactions_target_account_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('transactions_category_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('transactions_user_id_fkey', 'transactions', type_='foreignkey')
    op.create_foreign_key(None, 'transactions', 'accounts', ['account_id'], ['id'], referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'categories', ['category_id'], ['id'], referent_schema='finances', ondelete='SET NULL')
    op.create_foreign_key(None, 'transactions', 'users', ['user_id'], ['id'], referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'accounts', ['target_account_id'], ['id'], referent_schema='finances', ondelete='SET NULL')
    op.alter_column('users', 'telegram_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
    op.alter_column('users', 'telegram_username',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=100),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'telegram_username',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('users', 'telegram_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.create_foreign_key('transactions_user_id_fkey', 'transactions', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('transactions_category_id_fkey', 'transactions', 'categories', ['category_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('transactions_target_account_id_fkey', 'transactions', 'accounts', ['target_account_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('transactions_account_id_fkey', 'transactions', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'telegram_link_tokens', schema='finances', type_='foreignkey')
    op.create_foreign_key('telegram_link_tokens_user_id_fkey', 'telegram_link_tokens', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'categories', schema='finances', type_='foreignkey')
    op.create_foreign_key('categories_user_id_fkey', 'categories', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.create_foreign_key('budgets_user_id_fkey', 'budgets', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('budgets_category_id_fkey', 'budgets', 'categories', ['category_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'accounts', schema='finances', type_='foreignkey')
    op.create_foreign_key('accounts_user_id_fkey', 'accounts', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_table('telegram_user_state',
    sa.Column('chat_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('state', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('chat_id', name='telegram_user_state_pkey'),
    schema='bot'
    )
    op.create_table('finance_transactions',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('bot.finance_transactions_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('account_number', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('date_msk', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('time_msk', postgresql.TIME(), autoincrement=False, nullable=False),
    sa.Column('auth_code', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('category', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('amount', sa.NUMERIC(precision=15, scale=2), autoincrement=False, nullable=False),
    sa.Column('tx_type', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('balance', sa.NUMERIC(precision=15, scale=2), autoincrement=False, nullable=True),
    sa.Column('date_operation', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('merchant', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('telegram_id', sa.BIGINT(), autoincrement=False, nullable=True, comment='Telegram ID пользователя который загрузил выписку'),
    sa.Column('import_status', sa.VARCHAR(length=20), server_default=sa.text("'pending'::character varying"), autoincrement=False, nullable=False, comment='pending — не обработана, done — импортирована, error — ошибка импорта'),
    sa.Column('imported_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True, comment='Время когда ImportService обработал эту запись'),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='finance_transactions_pkey'),
    sa.UniqueConstraint('account_number', 'date_msk', 'time_msk', 'auth_code', 'amount', name='finance_transactions_unique'),
    schema='bot',
    comment='Сырые транзакции из банковских выписок, загруженных через Telegram бот'
    )
    op.create_index('ix_bot_ft_telegram_id_status', 'finance_transactions', ['telegram_id', 'import_status'], unique=False, schema='bot', postgresql_where="((import_status)::text = 'pending'::text)")
    op.create_index('ix_bot_ft_telegram_id', 'finance_transactions', ['telegram_id'], unique=False, schema='bot')
    op.create_index('ix_bot_ft_import_status', 'finance_transactions', ['import_status'], unique=False, schema='bot', postgresql_where="((import_status)::text = 'pending'::text)")
    op.create_index('ix_bot_ft_date_msk', 'finance_transactions', ['date_msk'], unique=False, schema='bot')
    op.create_table('telegram_upload_log',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('bot.telegram_upload_log_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('chat_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('file_name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('mime_type', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('file_size', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('accepted', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('reason', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='telegram_upload_log_pkey'),
    schema='bot'
    )
    # ### end Alembic commands ###
```
</document>

<document path="./alembic/versions/8aae31dde3c6_add_habits_tracker_models.py">
```py
"""add habits tracker models

Revision ID: 8aae31dde3c6
Revises: 9d1a9f3a7225
Create Date: 2026-03-26 16:47:36.654969+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8aae31dde3c6'
down_revision: Union[str, None] = '9d1a9f3a7225'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'accounts', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'categories', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'habit_logs', 'habits', ['habit_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'habits', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'telegram_link_tokens', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='SET NULL')
    op.create_foreign_key(None, 'transactions', 'transactions', ['linked_tx_id'], ['id'], source_schema='finances', referent_schema='finances')
    op.create_foreign_key(None, 'transactions', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'accounts', ['target_account_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='SET NULL')
    op.create_foreign_key(None, 'transactions', 'accounts', ['account_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'transactions', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'telegram_link_tokens', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'habits', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'habit_logs', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'categories', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'accounts', schema='finances', type_='foreignkey')
    # ### end Alembic commands ###
```
</document>

<document path="./alembic/versions/9d1a9f3a7225_.py">
```py
"""empty message

Revision ID: 9d1a9f3a7225
Revises: 002_enrichment, 4cae4220fc21
Create Date: 2026-03-26 16:47:18.737416+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d1a9f3a7225'
down_revision: Union[str, None] = ('002_enrichment', '4cae4220fc21')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
```
</document>

<document path="./alembic/versions/2a61cedac9c7_add_telegram_support.py">
```py
"""add_telegram_support

Revision ID: 2a61cedac9c7
Revises: 0ac212ee8ce1
Create Date: 2026-03-15 13:43:58.267974+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a61cedac9c7'
down_revision: Union[str, None] = '0ac212ee8ce1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('telegram_link_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=64), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('used', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['finances.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='finances'
    )
    op.create_index(op.f('ix_finances_telegram_link_tokens_token'), 'telegram_link_tokens', ['token'], unique=True, schema='finances')
    op.create_index(op.f('ix_finances_telegram_link_tokens_user_id'), 'telegram_link_tokens', ['user_id'], unique=False, schema='finances')
    op.drop_constraint('accounts_user_id_fkey', 'accounts', type_='foreignkey')
    op.create_foreign_key(None, 'accounts', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.drop_constraint('budgets_user_id_fkey', 'budgets', type_='foreignkey')
    op.drop_constraint('budgets_category_id_fkey', 'budgets', type_='foreignkey')
    op.create_foreign_key(None, 'budgets', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.drop_constraint('categories_user_id_fkey', 'categories', type_='foreignkey')
    op.create_foreign_key(None, 'categories', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.add_column('transactions', sa.Column('external_id', sa.String(length=100), nullable=True))
    op.add_column('transactions', sa.Column('import_source', sa.String(length=20), nullable=False))
    op.create_index(op.f('ix_transactions_external_id'), 'transactions', ['external_id'], unique=True)
    op.drop_constraint('transactions_target_account_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('transactions_category_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('transactions_account_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('transactions_user_id_fkey', 'transactions', type_='foreignkey')
    op.create_foreign_key(None, 'transactions', 'categories', ['category_id'], ['id'], referent_schema='finances', ondelete='SET NULL')
    op.create_foreign_key(None, 'transactions', 'users', ['user_id'], ['id'], referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'accounts', ['target_account_id'], ['id'], referent_schema='finances', ondelete='SET NULL')
    op.create_foreign_key(None, 'transactions', 'accounts', ['account_id'], ['id'], referent_schema='finances', ondelete='CASCADE')
    op.add_column('users', sa.Column('telegram_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('telegram_username', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_finances_users_telegram_id'), 'users', ['telegram_id'], unique=True, schema='finances')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_finances_users_telegram_id'), table_name='users', schema='finances')
    op.drop_column('users', 'telegram_username')
    op.drop_column('users', 'telegram_id')
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.create_foreign_key('transactions_user_id_fkey', 'transactions', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('transactions_account_id_fkey', 'transactions', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('transactions_category_id_fkey', 'transactions', 'categories', ['category_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('transactions_target_account_id_fkey', 'transactions', 'accounts', ['target_account_id'], ['id'], ondelete='SET NULL')
    op.drop_index(op.f('ix_transactions_external_id'), table_name='transactions')
    op.drop_column('transactions', 'import_source')
    op.drop_column('transactions', 'external_id')
    op.drop_constraint(None, 'categories', schema='finances', type_='foreignkey')
    op.create_foreign_key('categories_user_id_fkey', 'categories', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.drop_constraint(None, 'budgets', schema='finances', type_='foreignkey')
    op.create_foreign_key('budgets_category_id_fkey', 'budgets', 'categories', ['category_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('budgets_user_id_fkey', 'budgets', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'accounts', schema='finances', type_='foreignkey')
    op.create_foreign_key('accounts_user_id_fkey', 'accounts', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_finances_telegram_link_tokens_user_id'), table_name='telegram_link_tokens', schema='finances')
    op.drop_index(op.f('ix_finances_telegram_link_tokens_token'), table_name='telegram_link_tokens', schema='finances')
    op.drop_table('telegram_link_tokens', schema='finances')
    # ### end Alembic commands ###
```
</document>

