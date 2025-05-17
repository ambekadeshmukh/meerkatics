#!/bin/bash
# sentinelops/infrastructure/scripts/quick-deploy.sh

set -e

# Script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${BLUE}"
    echo "  _____            _   _            _ ____            "
   echo " / ____|          | | (_)          | |  _ \           "
   echo "| (___   ___ _ __ | |_ _ _ __   ___| | |_) | ___  ___ "
   echo " \___ \ / _ \ '_ \| __| | '_ \ / _ \ |  _ < / _ \/ __|"
   echo " ____) |  __/ | | | |_| | | | |  __/ | |_) | (_) \__ \\"
   echo "|_____/ \___|_| |_|\__|_|_| |_|\___|_|____/ \___/|___/"
   echo -e "${NC}"
   echo -e "${GREEN}LLM Observability Platform${NC}"
   echo
}

check_requirements() {
   echo -e "${BLUE}Checking system requirements...${NC}"
   
   # Check Docker
   if ! command -v docker &> /dev/null; then
       echo -e "${RED}Docker is not installed. Please install Docker and try again.${NC}"
       echo -e "Visit https://docs.docker.com/get-docker/ for installation instructions."
       exit 1
   fi
   
   # Check Docker Compose
   if ! command -v docker-compose &> /dev/null; then
       echo -e "${RED}Docker Compose is not installed. Please install Docker Compose and try again.${NC}"
       echo -e "Visit https://docs.docker.com/compose/install/ for installation instructions."
       exit 1
   fi
   
   # Check if Docker daemon is running
   if ! docker info &> /dev/null; then
        echo -e "${RED}Docker daemon is not running. Please start Docker and try again.${NC}"
        exit 1
   fi
   
   echo -e "${GREEN}All requirements are met!${NC}"
}

setup_environment() {
   echo -e "${BLUE}Setting up environment...${NC}"
   
   # Navigate to project root
   cd "${PROJECT_ROOT}"
   
   # Create .env file if it doesn't exist
   if [ ! -f "${PROJECT_ROOT}/infrastructure/.env" ]; then
       echo -e "${YELLOW}Creating default .env file...${NC}"
       cat > "${PROJECT_ROOT}/infrastructure/.env" << EOF
# Database settings
POSTGRES_USER=sentinelopsuser
POSTGRES_PASSWORD=sentinelopsdev
POSTGRES_DB=sentinelops
POSTGRES_PORT=5432

# API settings
API_PORT=8000
JWT_SECRET=$(openssl rand -hex 32)

# Frontend settings
FRONTEND_PORT=3000
API_URL=http://localhost:8000

# Prometheus settings
PROMETHEUS_PORT=9090
EOF
       echo -e "${GREEN}.env file created successfully!${NC}"
   else
       echo -e "${GREEN}.env file already exists, using existing configuration.${NC}"
   fi
}

start_services() {
   echo -e "${BLUE}Starting SentinelOps services...${NC}"
   
   cd "${PROJECT_ROOT}/infrastructure"
   
   # Pull latest images
   echo -e "${YELLOW}Pulling latest Docker images...${NC}"
   docker-compose pull
   
   # Start services
   echo -e "${YELLOW}Starting services...${NC}"
   docker-compose up -d
   
   echo -e "${GREEN}SentinelOps services started successfully!${NC}"
}

check_services() {
   echo -e "${BLUE}Checking service status...${NC}"
   
   cd "${PROJECT_ROOT}/infrastructure"
   
   # Wait for services to initialize
   echo -e "${YELLOW}Waiting for services to initialize (this may take a moment)...${NC}"
   sleep 10
   
   # Check if services are running
   if [ $(docker-compose ps -q | wc -l) -lt 5 ]; then
       echo -e "${RED}Some services failed to start. Please check the logs:${NC}"
       echo -e "${YELLOW}docker-compose logs${NC}"
       exit 1
   fi
   
   # Check API health
   API_PORT=$(grep API_PORT "${PROJECT_ROOT}/infrastructure/.env" | cut -d '=' -f2 || echo 8000)
   echo -e "${YELLOW}Checking API health on port ${API_PORT}...${NC}"
   
   MAX_RETRIES=30
   RETRY_COUNT=0
   
   while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
       if curl -s "http://localhost:${API_PORT}/v1/health" | grep -q "status.*ok"; then
           echo -e "${GREEN}API is healthy!${NC}"
           break
       else
           RETRY_COUNT=$((RETRY_COUNT + 1))
           if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
               echo -e "${RED}API health check failed after ${MAX_RETRIES} attempts.${NC}"
               echo -e "${YELLOW}Please check the logs: docker-compose logs api${NC}"
               exit 1
           fi
           echo -e "${YELLOW}API not ready yet, retrying in 2 seconds (${RETRY_COUNT}/${MAX_RETRIES})...${NC}"
           sleep 2
       fi
   done
   
   echo -e "${GREEN}All services are running!${NC}"
}

show_success() {
   # Get ports from .env file
   API_PORT=$(grep API_PORT "${PROJECT_ROOT}/infrastructure/.env" | cut -d '=' -f2 || echo 8000)
   FRONTEND_PORT=$(grep FRONTEND_PORT "${PROJECT_ROOT}/infrastructure/.env" | cut -d '=' -f2 || echo 3000)
   PROMETHEUS_PORT=$(grep PROMETHEUS_PORT "${PROJECT_ROOT}/infrastructure/.env" | cut -d '=' -f2 || echo 9090)
   
   echo -e "\n${GREEN}SentinelOps has been successfully deployed!${NC}\n"
   echo -e "Access the services:"
   echo -e "  - ${BLUE}Dashboard:${NC} http://localhost:${FRONTEND_PORT}"
   echo -e "  - ${BLUE}API:${NC} http://localhost:${API_PORT}"
   echo -e "  - ${BLUE}Prometheus:${NC} http://localhost:${PROMETHEUS_PORT}"
   echo
   echo -e "${YELLOW}To view logs:${NC}"
   echo -e "  docker-compose -f ${PROJECT_ROOT}/infrastructure/docker-compose.yml logs -f"
   echo
   echo -e "${YELLOW}To stop SentinelOps:${NC}"
   echo -e "  docker-compose -f ${PROJECT_ROOT}/infrastructure/docker-compose.yml down"
   echo
   echo -e "${YELLOW}To restart SentinelOps:${NC}"
   echo -e "  docker-compose -f ${PROJECT_ROOT}/infrastructure/docker-compose.yml restart"
   echo
   echo -e "${BLUE}For more information, visit:${NC}"
   echo -e "  https://github.com/your-username/sentinelops"
   echo
}

# Main execution
print_banner
check_requirements
setup_environment
start_services
check_services
show_success