#!/usr/bin/env python
"""Unified Project Management CLI."""
import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd, cwd=None, env=None):
    """Run a shell command."""
    try:
        if cwd:
            cwd = Path(cwd).resolve()
        result = subprocess.run(cmd, cwd=cwd, env=env, shell=True)
        return result.returncode
    except KeyboardInterrupt:
        return 130

def start():
    """Start the application containers."""
    print("🚀 Starting Backend-in-a-Box...")
    return run_command(["docker-compose", "up", "--build"])

def generate():
    """Run the code generator."""
    print("🏗️  Generating backend code...")
    return run_command([sys.executable, "-m", "generator"])

def migrate(args):
    """Run migration commands."""
    # Pass through to the existing migrate.py
    # We execute it inside the container if running, or locally if not?
    # For simplicity in this starter kit, let's assume local python env or docker exec.
    # But usually 'manage.py' is run by the user on host.
    
    # Ideally, we should check if docker is running and exec inside.
    # But simple approach: just run the migrate.py script which runs alembic.
    # Alembic needs DB verification.
    
    # Actually, the user experience "manage.py migrate" should probably 
    # run `docker-compose exec api python migrate.py` if docker is up.
    
    # Let's try to detect if we want to run inside docker or local.
    # For now, let's just forward to local migrate.py for simplicity, 
    # assuming user has dependencies OR they use 'manage.py' inside container?
    
    # Better: wrapper for docker-compose exec
    cmd = ["docker-compose", "exec", "api", "python", "migrate.py"] + args
    print(f"📦 Running migration in container: {' '.join(cmd)}")
    return run_command(cmd)

def test():
    """Run tests."""
    print("🧪 Running tests...")
    return run_command(["docker-compose", "exec", "api", "pytest"])

def help_text():
    print("""
🧰 Backend-in-a-Box CLI

Usage:
    python manage.py <command> [args]

Commands:
    start              Start application (Docker)
    generate           Generate code from schema
    migrate <args>     Run migration commands (inside Docker)
    test               Run tests
    help               Show this help

Examples:
    python manage.py start
    python manage.py generate
    python manage.py migrate generate "add user"
    python manage.py migrate upgrade
""")

def main():
    if len(sys.argv) < 2:
        help_text()
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "start":
        sys.exit(start())
    elif command == "generate":
        sys.exit(generate())
    elif command == "migrate":
        sys.exit(migrate(args))
    elif command == "test":
        sys.exit(test())
    else:
        help_text()
        sys.exit(1)

if __name__ == "__main__":
    main()
