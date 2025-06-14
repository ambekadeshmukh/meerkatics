#!/bin/bash
# meerkatics/infrastructure/aws/deploy.sh

set -e

# Script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
STACK_NAME="meerkatics"
REGION="us-east-1"
INSTANCE_TYPE="t3.medium"
SSH_LOCATION="0.0.0.0/0"
ACCESS_LOCATION="0.0.0.0/0"

print_banner() {
    echo -e "${BLUE}"
    echo
    echo "  _____            _   _            _ ____            "
    echo " / ____|          | | (_)          | |  _ \           "
    echo "| (___   ___ _ __ | |_ _ _ __   ___| | |_) | ___  ___ "
    echo " \___ \ / _ \ '_ \| __| | '_ \ / _ \ |  _ < / _ \/ __|"
    echo " ____) |  __/ | | | |_| | | | |  __/ | |_) | (_) \__ \\"
    echo "|_____/ \___|_| |_|\__|_|_| |_|\___|_|____/ \___/|___/"
    echo -e "${NC}"
    echo -e "${GREEN}AWS Deployment Script${NC}"
    echo
}

check_requirements() {
    echo -e "${BLUE}Checking requirements...${NC}"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}AWS CLI is not installed. Please install it and configure your credentials.${NC}"
        echo -e "Visit https://aws.amazon.com/cli/ for installation instructions."
        exit 1
    fi
    
    # Check if AWS CLI is configured
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}AWS CLI is not configured properly. Please run 'aws configure' first.${NC}"
        exit 1
    }
    
    echo -e "${GREEN}All requirements are met!${NC}"
}

prompt_for_parameters() {
    echo -e "${BLUE}Please provide the following parameters:${NC}"
    
    read -p "Stack name [$STACK_NAME]: " input
    STACK_NAME=${input:-$STACK_NAME}
    
    read -p "AWS Region [$REGION]: " input
    REGION=${input:-$REGION}
    
    read -p "EC2 Instance Type [$INSTANCE_TYPE]: " input
    INSTANCE_TYPE=${input:-$INSTANCE_TYPE}
    
    # Get available key pairs
    KEY_PAIRS=$(aws ec2 describe-key-pairs --region $REGION --query "KeyPairs[*].KeyName" --output text)
    
    if [ -z "$KEY_PAIRS" ]; then
        echo -e "${RED}No EC2 key pairs found in region $REGION. Please create a key pair first.${NC}"
        echo -e "You can create a key pair using the AWS Console or by running:"
        echo -e "aws ec2 create-key-pair --region $REGION --key-name YourKeyName --query 'KeyMaterial' --output text > YourKeyName.pem"
        exit 1
    fi
    
    echo -e "${YELLOW}Available key pairs in $REGION:${NC}"
    echo "$KEY_PAIRS" | tr '\t' '\n' | sed 's/^/- /'
    
    read -p "Key pair name: " KEY_NAME
    if ! echo "$KEY_PAIRS" | grep -q "$KEY_NAME"; then
        echo -e "${RED}Key pair '$KEY_NAME' not found in region $REGION.${NC}"
        exit 1
    fi
    
    read -p "IP range that can SSH to the instance [$SSH_LOCATION]: " input
    SSH_LOCATION=${input:-$SSH_LOCATION}
    
    read -p "IP range that can access Meerkatics services [$ACCESS_LOCATION]: " input
    ACCESS_LOCATION=${input:-$ACCESS_LOCATION}
    
    # Generate a secure password
    DB_PASSWORD=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9')
    echo -e "${YELLOW}Generated secure database password: $DB_PASSWORD${NC}"
    
    # Generate a secure JWT secret
    JWT_SECRET=$(openssl rand -hex 32)
    echo -e "${YELLOW}Generated secure JWT secret.${NC}"
}

deploy_stack() {
    echo -e "${BLUE}Deploying CloudFormation stack...${NC}"
    
    # Deploy CloudFormation stack
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://${SCRIPT_DIR}/cloudformation.yaml \
        --region $REGION \
        --parameters \
        ParameterKey=InstanceType,ParameterValue=$INSTANCE_TYPE \
        ParameterKey=KeyName,ParameterValue=$KEY_NAME \
        ParameterKey=SSHLocation,ParameterValue=$SSH_LOCATION \
        ParameterKey=AccessLocation,ParameterValue=$ACCESS_LOCATION \
        ParameterKey=DBPassword,ParameterValue=$DB_PASSWORD \
        ParameterKey=JWTSecret,ParameterValue=$JWT_SECRET \
        --capabilities CAPABILITY_IAM
    
    echo -e "${GREEN}CloudFormation stack deployment initiated!${NC}"
    echo -e "${YELLOW}Waiting for stack to complete (this may take 5-10 minutes)...${NC}"
    
    # Wait for stack to complete
    aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Stack deployment completed successfully!${NC}"
    else
        echo -e "${RED}Stack deployment failed. Please check the CloudFormation console for details.${NC}"
        exit 1
    fi
}

show_outputs() {
    echo -e "${BLUE}Deployment complete! Here are your Meerkatics endpoints:${NC}"
    
    # Get stack outputs
    OUTPUTS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs" --output json)
    
    # Extract and display each output
    echo "$OUTPUTS" | jq -r '.[] | "\(.Description): \(.Value)"'
    
    echo
    echo -e "${YELLOW}IMPORTANT: Save these credentials securely:${NC}"
    echo -e "  - Database Password: $DB_PASSWORD"
    echo -e "  - JWT Secret: $JWT_SECRET"
    echo
    echo -e "${YELLOW}To delete the stack:${NC}"
    echo -e "  aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION"
    echo
}

# Main execution
print_banner
check_requirements
prompt_for_parameters
deploy_stack
show_outputs