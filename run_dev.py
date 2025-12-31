#!/usr/bin/env python
"""Development server runner - for quick local testing without Docker."""
import subprocess
import sys

def main():
    """Run the development server."""
    print("🔧 Starting Backend-in-a-Box development server...")
    print("⚠️  Note: This requires PostgreSQL and Redis running locally")
    print("   For full Docker setup, use: docker-compose up\n")
    
    try:
        subprocess.run([
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except FileNotFoundError:
        print("❌ uvicorn not found. Install dependencies first:")
        print("   poetry install")
        print("   OR")
        print("   pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
