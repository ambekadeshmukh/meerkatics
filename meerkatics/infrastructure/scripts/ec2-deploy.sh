#!/bin/bash

# Meerkatics EC2 Deployment Script
# This script helps deploy Meerkatics on an EC2 instance

set -e

# Text formatting
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}This script must be run as root or with sudo${NC}"
    exit 1
fi

echo -e "${GREEN}=== Meerkatics EC2 Deployment Script ===${NC}"
echo "This script will set up Meerkatics on your EC2 instance"

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
apt-get update
apt-get install -y docker.io docker-compose git

# Start Docker service
echo -e "\n${YELLOW}Starting Docker service...${NC}"
systemctl start docker
systemctl enable docker

# Clone repository if not already cloned
if [ ! -d "/opt/meerkatics" ]; then
    echo -e "\n${YELLOW}Cloning Meerkatics repository...${NC}"
    git clone https://github.com/your-username/meerkatics.git /opt/meerkatics
else
    echo -e "\n${YELLOW}Meerkatics repository already exists, pulling latest changes...${NC}"
    cd /opt/meerkatics
    git pull
fi

# Create .env file
echo -e "\n${YELLOW}Creating .env file...${NC}"
cat > /opt/meerkatics/.env << EOF
# Core Configuration
API_PORT=8000
JWT_SECRET=$(openssl rand -hex 32)
FRONTEND_PORT=3000
API_URL=http://localhost:8000
PROMETHEUS_PORT=9090
ENVIRONMENT=production

# File Storage Configuration
FILE_STORAGE_PATH=/data/storage

# API Key (used for authentication)
API_KEY_SECRET=$(openssl rand -hex 16)
EOF

# Start application
echo -e "\n${YELLOW}Starting Meerkatics...${NC}"
cd /opt/meerkatics/infrastructure
docker-compose up -d

# Check if services are running
echo -e "\n${YELLOW}Checking if services are running...${NC}"
sleep 10
if docker-compose ps | grep -q "Up"; then
    echo -e "\n${GREEN}Meerkatics has been successfully deployed!${NC}"
    echo -e "Frontend URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"
    echo -e "API URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
    echo -e "Prometheus URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):9090"
    echo -e "\nAPI Key: $(grep API_KEY_SECRET /opt/meerkatics/.env | cut -d= -f2)"
else
    echo -e "\n${RED}There was an issue deploying Meerkatics. Please check the logs with 'docker-compose logs'${NC}"
fi

echo -e "\n${YELLOW}To view logs: ${NC}cd /opt/meerkatics/infrastructure && docker-compose logs -f"
echo -e "${YELLOW}To stop the application: ${NC}cd /opt/meerkatics/infrastructure && docker-compose down"
