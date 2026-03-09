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

