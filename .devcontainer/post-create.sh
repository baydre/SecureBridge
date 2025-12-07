#!/bin/bash

# Post-create script for SecureBridge dev container
# This script runs after the container is created

set -e

echo "🚀 Running post-create setup for SecureBridge..."

# Ensure we're in the workspace directory
cd /workspace

# Install Python dependencies (in case they weren't fully installed)
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt --quiet

# Install development dependencies
echo "🔧 Installing development dependencies..."
pip install pytest pytest-asyncio httpx black ruff --quiet

# Generate secure keys if they don't exist
if [ ! -f ".env" ]; then
    echo "🔑 Generating secure keys..."
    python generate_keys.py
    
    echo "📝 Setting up environment file..."
    cp .env.example .env
    
    # Note: Users will need to manually add the generated keys to .env
    echo "⚠️  Please add the generated keys from the output above to your .env file"
else
    echo "✅ .env file already exists"
fi

# Create database directory if it doesn't exist
mkdir -p /workspace/data

# Set proper permissions
chmod +x generate_keys.py

echo ""
echo "✅ Dev container setup complete!"
echo ""
echo "📚 Quick Start Commands:"
echo "  - Run app:        uvicorn app.main:app --reload"
echo "  - Run tests:      pytest tests/ -v"
echo "  - Format code:    black app/ tests/"
echo "  - Lint code:      ruff check app/ tests/"
echo "  - Generate keys:  python generate_keys.py"
echo ""
echo "🌐 The app will be available at:"
echo "  - http://localhost:8000"
echo "  - http://localhost:8000/docs (API documentation)"
echo ""
