#!/usr/bin/env python
"""Database migration management CLI."""
import sys
import subprocess
from pathlib import Path


def run_alembic(args: list[str]) -> int:
    """Run alembic command."""
    cmd = ["alembic"] + args
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def init():
    """Initialize database with current schema."""
    print("🗄️  Initializing database...")
    
    # Run migrations
    print("📦 Running migrations...")
    code = run_alembic(["upgrade", "head"])
    
    if code == 0:
        print("✅ Database initialized successfully!")
    else:
        print("❌ Database initialization failed")
        sys.exit(code)


def generate(message: str):
    """Generate a new migration."""
    if not message:
        print("❌ Error: Migration message required")
        print("Usage: python migrate.py generate 'your message here'")
        sys.exit(1)
    
    print(f"🔍 Detecting schema changes...")
    code = run_alembic(["revision", "--autogenerate", "-m", message])
    
    if code == 0:
        print("✅ Migration generated successfully!")
        print("📝 Review the migration file in migrations/versions/")
        print("🚀 Apply with: python migrate.py upgrade")
    else:
        print("❌ Migration generation failed")
        sys.exit(code)


def upgrade():
    """Apply all pending migrations."""
    print("⬆️  Applying migrations...")
    code = run_alembic(["upgrade", "head"])
    
    if code == 0:
        print("✅ Migrations applied successfully!")
    else:
        print("❌ Migration failed")
        sys.exit(code)


def downgrade(steps: int = 1):
    """Rollback migrations."""
    print(f"⬇️  Rolling back {steps} migration(s)...")
    code = run_alembic(["downgrade", f"-{steps}"])
    
    if code == 0:
        print("✅ Rollback successful!")
    else:
        print("❌ Rollback failed")
        sys.exit(code)


def status():
    """Show migration status."""
    print("📊 Migration status:")
    run_alembic(["current"])
    print("\n📜 Migration history:")
    run_alembic(["history"])


def help_text():
    """Show help text."""
    print("""
🗄️  Database Migration Manager

Usage:
    python migrate.py <command> [args]

Commands:
    init                    Initialize database with current schema
    generate "message"      Generate new migration from schema changes
    upgrade                 Apply all pending migrations
    downgrade [steps]       Rollback migrations (default: 1)
    status                  Show current migration status
    help                    Show this help message

Examples:
    python migrate.py init
    python migrate.py generate "add phone number to user"
    python migrate.py upgrade
    python migrate.py downgrade 2
    python migrate.py status
""")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        help_text()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        init()
    elif command == "generate":
        message = sys.argv[2] if len(sys.argv) > 2 else ""
        generate(message)
    elif command == "upgrade":
        upgrade()
    elif command == "downgrade":
        steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        downgrade(steps)
    elif command == "status":
        status()
    elif command == "help":
        help_text()
    else:
        print(f"❌ Unknown command: {command}")
        help_text()
        sys.exit(1)


if __name__ == "__main__":
    main()
