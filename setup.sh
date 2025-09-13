#!/bin/bash
# Setup script for GOFAP - Government Operations and Financial Accounting Platform

set -e

echo "🏛️  Setting up GOFAP - Government Operations and Financial Accounting Platform"
echo "=================================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install basic requirements first
echo "📋 Installing basic dependencies..."
pip install --upgrade pip
pip install Flask==2.3.3 Flask-SQLAlchemy==3.0.5 requests==2.31.0

# Install full requirements if available
if [ -f "requirements.txt" ]; then
    echo "📋 Installing full dependencies from requirements.txt..."
    pip install -r requirements.txt || echo "⚠️  Some dependencies may have failed to install"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p instance

# Copy environment template if .env doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        echo "⚙️  Copying environment template..."
        cp .env.template .env
        echo "📝 Please edit .env file with your configuration values"
    fi
fi

# Initialize database
echo "🗄️  Initializing database..."
export FLASK_APP=main.py
export FLASK_ENV=development
python3 -c "
from main import app, db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"

echo ""
echo "🎉 GOFAP setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys and configuration"
echo "2. Run the application with: python3 main.py"
echo "3. Visit http://localhost:5000 to access GOFAP"
echo ""
echo "For development:"
echo "- Activate venv: source venv/bin/activate"
echo "- Run Flask dev server: flask run --debug"
echo ""
echo "📞 Support: (844) 697-7877 ext 6327"
echo "📧 Email: gofap@ofaps.spurs.gov"
echo "🏛️  Office of Finance, Accounting, and Procurement Services (OFAPS)"
echo "    \"We Account for Everything\""