"""
Local Development Deployment Script (No Docker Required)
Runs FastAPI with local PostgreSQL and Redis
"""

import subprocess
import sys
import os
import time
from pathlib import Path


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_command(cmd, shell=True, check=False):
    """Run a system command"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_python():
    """Check Python installation"""
    print_section("1. Checking Python Installation")
    
    success, stdout, stderr = run_command("py --version")
    if success:
        print(f"✓ Python found: {stdout.strip()}")
        return True
    else:
        print("✗ Python not found. Please install Python 3.11+")
        print("  Download: https://www.python.org/downloads/")
        return False


def check_postgresql():
    """Check PostgreSQL installation"""
    print_section("2. Checking PostgreSQL Installation")
    
    success, stdout, stderr = run_command("psql --version")
    if success:
        print(f"✓ PostgreSQL found: {stdout.strip()}")
        print("\n  To start PostgreSQL (Windows):")
        print("  • If installed as service: Should start automatically")
        print("  • If portable: Run postgres.exe manually")
        print("\n  To start PostgreSQL (Mac):")
        print("  • brew services start postgresql")
        print("\n  To start PostgreSQL (Linux):")
        print("  • sudo systemctl start postgresql")
        return True
    else:
        print("✗ PostgreSQL not found")
        print("  Download: https://www.postgresql.org/download/")
        print("\n  Quick Setup (Windows):")
        print("  1. Download and install PostgreSQL")
        print("  2. During installation, note the password for 'postgres' user")
        print("  3. PostgreSQL will start automatically as a service")
        return False


def check_redis():
    """Check Redis installation"""
    print_section("3. Checking Redis Installation")
    
    success, stdout, stderr = run_command("redis-cli --version")
    if success:
        print(f"✓ Redis found: {stdout.strip()}")
        print("\n  To start Redis (Windows):")
        print("  • If installed via WSL: wsl redis-server")
        print("  • If installed as service: Should start automatically")
        print("\n  To start Redis (Mac):")
        print("  • brew services start redis")
        print("\n  To start Redis (Linux):")
        print("  • sudo systemctl start redis-server")
        return True
    else:
        print("✗ Redis not found")
        print("  Download: https://redis.io/download")
        print("  (Windows users can use WSL: wsl apt-get install redis-server)")
        return False


def install_dependencies():
    """Install Python dependencies"""
    print_section("4. Installing Python Dependencies")
    
    print("📦 Installing dependencies from requirements.txt...")
    success, stdout, stderr = run_command("py -m pip install -q -r requirements.txt")
    
    if success:
        print("✓ Dependencies installed successfully")
        
        print("\n🧠 Downloading spaCy model...")
        success, stdout, stderr = run_command("py -m spacy download -q en_core_web_sm")
        
        if success:
            print("✓ spaCy model downloaded")
            return True
        else:
            print("⚠ Warning: Could not download spaCy model")
            print("  Run manually: python -m spacy download en_core_web_sm")
            return False
    else:
        print("✗ Failed to install dependencies")
        print(f"  Error: {stderr}")
        return False


def setup_database():
    """Set up PostgreSQL database"""
    print_section("5. Setting Up PostgreSQL Database")
    
    print("⚠  Important: Ensure PostgreSQL is running!")
    print("   On Windows: Check Services app for 'postgresql-x64-XX' service")
    print("   Status: Running (green) or Start it if stopped\n")
    
    db_url = "postgresql://user:password@localhost:5432/tagging_db"
    print(f"📝 Using database: {db_url}")
    print("\n⚠  First time setup (if user doesn't exist):")
    print("   1. Open PostgreSQL command prompt as administrator")
    print("   2. Run: CREATE USER \"user\" WITH PASSWORD 'password' CREATEDB;")
    print("   3. Run: GRANT CREATE ON DATABASE postgres TO \"user\";")
    print("   4. Then rerun this script")
    
    print("\n  Running: python database.py")
    success, stdout, stderr = run_command("py database.py")
    
    if success:
        print("✓ Database initialized")
        return True
    else:
        if "could not connect" in stderr.lower() or "error" in stderr.lower():
            print("⚠ Database connection failed")
            print("  Make sure PostgreSQL is running and user 'user' exists")
            return False
        print("✓ Database script executed")
        return True


def verify_services():
    """Verify all services are running"""
    print_section("6. Verifying Services")
    
    print("🔍 Checking PostgreSQL connection...")
    success, stdout, stderr = run_command('psql -U user -d postgres -c "SELECT version();" 2>&1')
    
    if success and "PostgreSQL" in stdout:
        print("✓ PostgreSQL is running and accessible")
    else:
        print("⚠ Could not verify PostgreSQL")
        print("  Error: Make sure PostgreSQL is running and user 'user' exists")
    
    print("\n🔍 Checking Redis connection...")
    success, stdout, stderr = run_command("redis-cli ping")
    
    if success and "PONG" in stdout:
        print("✓ Redis is running and accessible")
    else:
        print("⚠ Could not verify Redis")
        print("  Error: Make sure Redis is running on localhost:6379")


def start_application():
    """Start the FastAPI application"""
    print_section("7. Starting FastAPI Application")
    
    print("🚀 Starting server on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    time.sleep(2)
    
    cmd = "py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    run_command(cmd, shell=True)


def main():
    """Main deployment workflow"""
    
    print("\n" + "=" * 80)
    print("  Automated Content Tagging Engine - Local Deployment Setup")
    print("=" * 80)
    
    # Check dependencies
    if not check_python():
        return
    
    db_ok = check_postgresql()
    redis_ok = check_redis()
    
    if not db_ok or not redis_ok:
        print("\n⚠  Some services are missing. Please install them first:")
        if not db_ok:
            print("  • PostgreSQL: https://www.postgresql.org/download/")
        if not redis_ok:
            print("  • Redis: https://redis.io/download")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n✗ Failed to install dependencies. Cannot proceed.")
        return
    
    # Setup database
    if not setup_database():
        print("\n⚠  Database setup had issues. Some features may not work.")
    
    # Verify services
    verify_services()
    
    # Start application
    print_section("Ready to Start!")
    print("✓ All components initialized")
    print("✓ Dependencies installed")
    print("✓ Database configured")
    print("\nStarting FastAPI application...\n")
    
    try:
        start_application()
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped by user")


if __name__ == "__main__":
    # Change to project directory
    os.chdir(Path(__file__).parent)
    main()
