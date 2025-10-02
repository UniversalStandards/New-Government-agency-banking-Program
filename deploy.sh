#!/bin/bash

# GOFAP Deployment Script
# Production deployment script for Government Operations and Financial Accounting Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="gofap"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

echo -e "${GREEN}🚀 Starting GOFAP Deployment${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  Creating .env file from template...${NC}"
    cat > "$ENV_FILE" << EOF
# GOFAP Environment Configuration
SECRET_KEY=$(openssl rand -hex 32)
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
MODERN_TREASURY_API_KEY=your_modern_treasury_api_key_here
MODERN_TREASURY_ORG_ID=your_modern_treasury_org_id_here
FLASK_ENV=production
DEBUG=False
EOF
    echo -e "${YELLOW}⚠️  Please update the .env file with your actual API keys before continuing.${NC}"
    read -p "Press Enter to continue after updating .env file..."
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p logs uploads ssl

# Set proper permissions
chmod 755 logs uploads ssl

# Build and start services
echo -e "${YELLOW}🔨 Building and starting services...${NC}"
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check if services are running
echo -e "${YELLOW}🔍 Checking service status...${NC}"
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Services are running successfully!${NC}"
else
    echo -e "${RED}❌ Some services failed to start. Check logs with: docker-compose logs${NC}"
    exit 1
fi

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
docker-compose exec web flask db upgrade

# Create admin user
echo -e "${YELLOW}👤 Creating admin user...${NC}"
docker-compose exec web python -c "
from main import app, db
from models import User, UserRole
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@gofap.gov',
            first_name='System',
            last_name='Administrator',
            role=UserRole.ADMIN,
            department='IT'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully')
    else:
        print('Admin user already exists')
"

# Health check
echo -e "${YELLOW}🏥 Performing health check...${NC}"
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Health check failed, but services may still be starting up.${NC}"
fi

# Display access information
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}📋 Access Information:${NC}"
echo -e "   🌐 Web Application: http://localhost"
echo -e "   🔧 Admin Panel: http://localhost/auth/login"
echo -e "   📊 API Documentation: http://localhost/api/v1/health"
echo -e "   🗄️  Database: localhost:5432"
echo -e ""
echo -e "${YELLOW}🔐 Default Admin Credentials:${NC}"
echo -e "   Username: admin"
echo -e "   Password: admin123"
echo -e "   ${RED}⚠️  Please change the admin password immediately!${NC}"
echo -e ""
echo -e "${GREEN}📝 Useful Commands:${NC}"
echo -e "   View logs: docker-compose logs -f"
echo -e "   Stop services: docker-compose down"
echo -e "   Restart services: docker-compose restart"
echo -e "   Update services: docker-compose pull && docker-compose up -d"
echo -e ""
echo -e "${GREEN}🔒 Security Recommendations:${NC}"
echo -e "   1. Change default admin password"
echo -e "   2. Update API keys in .env file"
echo -e "   3. Configure SSL certificates in ssl/ directory"
echo -e "   4. Set up proper firewall rules"
echo -e "   5. Enable database backups"