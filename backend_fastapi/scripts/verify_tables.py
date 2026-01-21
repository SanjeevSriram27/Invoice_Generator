"""
Verify database tables are created correctly
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import engine
from sqlalchemy import text


async def verify_tables():
    """Check if all tables are created in PostgreSQL"""
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        )
        tables = [row[0] for row in result]

        print("OK - Database tables created successfully:")
        for table in tables:
            print(f"  - {table}")

        # Check expected tables
        expected_tables = {
            'alembic_version',
            'business_profiles',
            'invoice_number_sequences',
            'invoices',
            'invoice_items'
        }

        created_tables = set(tables)
        missing = expected_tables - created_tables

        if missing:
            print(f"\nWARNING - Missing tables: {missing}")
            return False
        else:
            print(f"\nSUCCESS - All {len(expected_tables)} tables created successfully!")
            return True


if __name__ == "__main__":
    success = asyncio.run(verify_tables())
    sys.exit(0 if success else 1)
