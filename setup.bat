@echo off
REM Setup script for Automated Content Tagging Engine (Windows)

echo 🚀 Setting up Automated Content Tagging Engine...

REM Check Python version
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📥 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Download spaCy model
echo 🧠 Downloading spaCy model...
python -m spacy download en_core_web_sm

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️  Creating .env file...
    copy .env.example .env
    echo ⚠️  Please update .env with your database and Redis configuration
)

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Update .env with your database and Redis settings
echo 2. Run: uvicorn app.main:app --reload
echo 3. Visit: http://localhost:8000/docs
echo.
