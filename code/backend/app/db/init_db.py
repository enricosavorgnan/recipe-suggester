"""
Database initialization using Alembic migrations
Run: alembic upgrade head
"""
import subprocess
import sys


def init_db():
    """Run database migrations"""
    print("Running database migrations...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✓ Database migrations applied successfully!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Migration failed: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("✗ Alembic not found. Install with: pip install alembic")
        sys.exit(1)


if __name__ == "__main__":
    init_db()
