# SentinelOps Installation Guide

This guide provides detailed instructions for installing and configuring SentinelOps in various environments, from development setups to production deployments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [SDK Installation](#sdk-installation)
3. [Development Setup (Docker Compose)](#development-setup-docker-compose)
4. [Production Setup (Kubernetes)](#production-setup-kubernetes)
5. [AWS Deployment](#aws-deployment)
6. [Custom Deployment](#custom-deployment)
7. [Configuration](#configuration)
8. [Upgrading](#upgrading)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimal (Development):**
- 2 CPU cores
- 4GB RAM
- 20GB storage
- Docker Engine 20.10+ or Kubernetes 1.19+

**Recommended (Production):**
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ storage
- Kubernetes 1.22+ or Docker Swarm
- PostgreSQL 13+
- Object storage (S3-compatible)

### Software Requirements

- **Docker**: Required for container-based deployments
- **Docker Compose**: Required for development setup
- **kubectl**: Required for Kubernetes deployments
- **Helm**: Required for Kubernetes deployments
- **Python 3.8+**: Required for SDK usage
- **Git**: Required for source code management

### Network Requirements

- **Outbound access**: Required for SDK to send telemetry data
- **Inbound ports**: 80/443 for web UI, 8000 for API server
- **Internal communication**: Various ports for component communication

## SDK Installation

The SentinelOps SDK can be installed via pip for Python applications:

```bash
pip install sentinelops
```

For other languages, see the language-specific installation instructions:

- [JavaScript/TypeScript Installation](./javascript-installation.md)
- [Java Installation](./java-installation.md) (coming soon)
- [Go Installation](./go-installation.md) (coming soon)

## Development Setup (Docker Compose)

For local development and testing, the easiest way to get started is with Docker Compose.

### Quick Setup with Script

```bash
# Clone the repository
git clone https://github.com/sentinelops/sentinelops.git
cd sentinelops

# Run the quick deployment script
./infrastructure/scripts/quick-deploy.sh
```

This script will:
1. Check prerequisites
2. Set up the environment
3. Create necessary configuration files
4. Start all services with Docker Compose
5. Perform health checks

Once complete, you can access:
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- Prometheus: http://localhost:9090

### Manual Setup

If you prefer to set up manually:

1. Clone the repository:
   ```bash
   git clone https://github.com/sentinelops/sentinelops.git
   cd sentinelops
   ```

2. Create a `.env` file in the `infrastructure` directory:
   ```bash
   cp infrastructure/.env.example infrastructure/.env
   ```

3. Edit the `.env` file to configure your environment:
   ```bash
   # Open with your favorite editor
   vim infrastructure/.env
   ```

4. Start the services:
   ```bash
   cd infrastructure
   docker-compose up -d
   ```

5. Check service status:
   ```bash
   docker-compose ps
   ```

### Configuration Options

The development setup can be customized through several options in the `.env` file:

- `DEPLOYMENT_MODE`: Set to `minimal`, `standard`, or `full` to control which components are deployed
- `RETENTION_DAYS`: Number of days to retain data (default: 30)
- `ENABLE_PROMETHEUS`: Enable/disable Prometheus metrics (default: true)
- `ENABLE_HALLUCINATION_DETECTION`: Enable/disable hallucination detection (default: true)
- `ENABLE_COST_OPTIMIZATION`: Enable/disable cost optimization features (default: true)

See the [Configuration](#configuration) section for more details.

## Production Setup (Kubernetes)

For production environments, Kubernetes is the recommended deployment platform.

### Prerequisites

- Kubernetes cluster (1.22+)
- Helm (3.0+)
- kubectl configured to access your cluster
- Storage class for persistent volumes
- Load balancer or ingress controller

### Installation with Helm

1. Add the SentinelOps Helm repository:
   ```bash
   helm repo add sentinelops https://charts.sentinelops.io
   helm repo update
   ```

2. Create a values file for your configuration:
   ```bash
   cp values.yaml.example my-values.yaml
   # Edit my-values.yaml with your configuration
   ```

3. Install SentinelOps:
   ```bash
   helm install sentinelops sentinelops/sentinelops \
     --namespace monitoring \
     --create-namespace \
     --values my-values.yaml
   ```

4. Verify the installation:
   ```bash
   kubectl get pods -n monitoring
   ```

### Custom Configuration

For production deployments, you should customize the Helm values to match your requirements:

```yaml
global:
  # Environment settings
  environment: production
  
  # Storage settings
  storage:
    class: managed-premium
    size: 50Gi
  
  # Security settings
  security:
    enableTLS: true
    createCertificate: true
    
  # Retention settings
  retention:
    metrics: 90  # days
    requests: 30  # days
    rawData: 7    # days
    
# Component-specific settings
api:
  replicas: 2
  resources:
    requests:
      cpu: 1
      memory: 2Gi
    limits:
      cpu: 2
      memory: 4Gi

database:
  replicas: 3
  resources:
    requests:
      cpu: 2
      memory: 4Gi
    limits:
      cpu: 4
      memory: 8Gi

# Additional components...
```

See the [Helm Chart Reference](./helm-chart-reference.md) for complete configuration options.

### High Availability Setup

For high availability in production:

1. Ensure your values file includes:
   ```yaml
   global:
     highAvailability: true
     
   api:
     replicas: 3
     
   database:
     replicas: 3
     
   kafka:
     replicas: 3
     
   prometheus:
     replicas: 2
   ```

2. Install or upgrade with the HA values:
   ```bash
   helm upgrade --install sentinelops sentinelops/sentinelops \
     --namespace monitoring \
     --values my-ha-values.yaml
   ```

## AWS Deployment

SentinelOps provides simplified deployment for AWS environments.

### CloudFormation Deployment

1. Navigate to the AWS directory:
   ```bash
   cd infrastructure/aws
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

3. Follow the interactive prompts to configure your deployment:
   - Stack name
   - AWS Region
   - Instance type
   - Key pair name
   - Security settings

4. The script will create a CloudFormation stack and deploy SentinelOps.

5. Once completed, the script will output:
   - Dashboard URL
   - API URL
   - SSH command to connect to the instance

### Manual AWS Setup

If you prefer manual deployment:

1. Navigate to the AWS CloudFormation console.

2. Create a new stack using the template file:
   `infrastructure/aws/cloudformation.yaml`

3. Configure the parameters:
   - Stack name
   - Instance type
   - Key pair
   - Security settings

4. Create the stack and wait for completion.

### AWS Configuration Options

For AWS deployments, you can configure:

- **InstanceType**: EC2 instance type (t3.medium recommended for minimal setup)
- **KeyName**: EC2 key pair for SSH access
- **VpcId**: Existing VPC ID (optional)
- **SubnetId**: Existing subnet ID (optional)
- **SecurityGroupId**: Existing security group ID (optional)
- **DBPassword**: PostgreSQL password
- **JWTSecret**: Secret for JWT tokens

## Custom Deployment

For custom environments or advanced deployments:

### Component-Based Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/sentinelops/sentinelops.git
   cd sentinelops
   ```

2. Build the components:
   ```bash
   # Build API server
   cd backend/api-server
   docker build -t sentinelops/api-server:latest .
   
   # Build data processor
   cd ../data-processor
   docker build -t sentinelops/data-processor:latest .
   
   # Build frontend
   cd ../../frontend
   docker build -t sentinelops/frontend:latest .
   ```

3. Deploy each component according to your infrastructure.

### Cloud Deployment (GCP, Azure)

For GCP or Azure deployments, follow the platform-specific guides:

- [GCP Deployment Guide](./gcp-deployment.md)
- [Azure Deployment Guide](./azure-deployment.md)

## Configuration

### Environment Variables

SentinelOps components can be configured using environment variables:

#### API Server

```
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=sentinelopsuser
POSTGRES_PASSWORD=sentinelopspassword
POSTGRES_DB=sentinelops
API_PORT=8000
JWT_SECRET=your-secret-key
LOG_LEVEL=info
ENABLE_PROMETHEUS=true
```

#### Data Processor

```
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=sentinelopsuser
POSTGRES_PASSWORD=sentinelopspassword
POSTGRES_DB=sentinelops
ENABLE_HALLUCINATION_DETECTION=true
ENABLE_COST_OPTIMIZATION=true
```

#### Frontend

```
API_URL=http://api:8000
```

### Configuration Files

For more advanced configuration, use configuration files:

#### API Server Config

```yaml
# config.yaml
server:
  host: 0.0.0.0
  port: 8000
  debug: false
  cors_origins:
    - http://localhost:3000
    - http://localhost

database:
  host: postgres
  port: 5432
  username: sentinelopsuser
  password: sentinelopspassword
  database: sentinelops

auth:
  jwt_secret: your-secret-key
  token_expiry: 86400  # 24 hours
  refresh_expiry: 604800  # 7 days

logging:
  level: info
  format: json
  path: /var/log/sentinelops

prometheus:
  enabled: true
  path: /metrics
```

#### SDK Config

```yaml
# sentinelops.yaml
monitoring:
  api_url: https://your-sentinelops-instance.com/api
  api_key: your-api-key
  
  # Optional configuration
  environment: production
  sampling_rate: 1.0  # 100%
  batch_size: 10
  flush_interval: 5  # seconds
  log_requests: true
  log_responses: true
```

## Upgrading

### Docker Compose Upgrade

To upgrade a Docker Compose deployment:

1. Pull the latest changes:
   ```bash
   cd sentinelops
   git pull
   ```

2. Update your environment file if needed:
   ```bash
   # Check for new configuration options
   diff infrastructure/.env.example infrastructure/.env
   ```

3. Rebuild and restart the services:
   ```bash
   cd infrastructure
   docker-compose down
   docker-compose pull
   docker-compose up -d
   ```

### Kubernetes Upgrade

To upgrade a Kubernetes deployment:

1. Update the Helm repository:
   ```bash
   helm repo update
   ```

2. Check for changes in values:
   ```bash
   helm show values sentinelops/sentinelops > new-values.yaml
   # Compare with your existing values file
   ```

3. Upgrade the deployment:
   ```bash
   helm upgrade sentinelops sentinelops/sentinelops \
     --namespace monitoring \
     --values my-values.yaml
   ```

## Troubleshooting

### Common Issues

#### Services Not Starting

**Problem**: Docker Compose services fail to start.

**Solution**:
1. Check if ports are already in use:
   ```bash
   netstat -tuln
   ```
2. Check service logs:
   ```bash
   docker-compose logs api
   docker-compose logs postgres
   ```
3. Verify environment variables in `.env` file.

#### Database Connection Issues

**Problem**: Services cannot connect to the database.

**Solution**:
1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   ```
2. Verify database credentials in environment variables.
3. Check database logs:
   ```bash
   docker-compose logs postgres
   ```

#### API Connection Issues

**Problem**: Frontend cannot connect to API server.

**Solution**:
1. Check if API server is running:
   ```bash
   docker-compose ps api
   ```
2. Verify API URL configuration.
3. Check for CORS issues in browser console.
4. Ensure network connectivity between components.

#### Kubernetes Pod Issues

**Problem**: Pods remain in "Pending" or "CrashLoopBackOff" state.

**Solution**:
1. Check pod status and events:
   ```bash
   kubectl describe pod -n monitoring <pod-name>
   ```
2. Check pod logs:
   ```bash
   kubectl logs -n monitoring <pod-name>
   ```
3. Verify persistent volume claims:
   ```bash
   kubectl get pvc -n monitoring
   ```

### Getting Help

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](./troubleshooting.md) for detailed solutions.
2. Visit the [SentinelOps GitHub repository](https://github.com/sentinelops/sentinelops/issues) to search for known issues.
3. Join our [Discord community](https://discord.gg/sentinelops) for community support.
4. Open a GitHub issue with detailed information about your problem.

For enterprise support, contact [support@sentinelops.com](mailto:support@sentinelops.com).