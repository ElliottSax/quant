#!/bin/bash

# Setup script for ML infrastructure
# Run this after setting up the main application

set -e

echo "==================================="
echo "Quant ML Infrastructure Setup"
echo "==================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running from project root
if [ ! -d "quant/backend" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Step 1: Install ML Python dependencies
echo -e "${GREEN}Step 1: Installing ML Python dependencies...${NC}"
cd quant/backend
pip install -r requirements-ml.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ ML dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install ML dependencies${NC}"
    exit 1
fi
cd ../..

# Step 2: Create necessary directories
echo -e "${GREEN}Step 2: Creating directories...${NC}"
mkdir -p quant/backend/models
mkdir -p quant/backend/ml_data
mkdir -p quant/backend/experiments
echo -e "${GREEN}✓ Directories created${NC}"

# Step 3: Set up environment variables
echo -e "${GREEN}Step 3: Setting up environment variables...${NC}"
if [ ! -f "quant/.env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from template...${NC}"
    cp quant/.env.example quant/.env
fi

# Add ML-specific environment variables if not present
if ! grep -q "ML_" quant/.env; then
    cat >> quant/.env << EOF

# ML Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
ML_MODEL_CACHE_DIR=./models
ML_RANDOM_SEED=42
ML_USE_GPU=false

# MinIO (for MLFlow artifacts)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin

# MLFlow Database
MLFLOW_DB=mlflow
EOF
    echo -e "${GREEN}✓ ML environment variables added${NC}"
else
    echo -e "${GREEN}✓ ML environment variables already present${NC}"
fi

# Step 4: Start ML services with Docker
echo -e "${GREEN}Step 4: Starting ML services...${NC}"
echo -e "${YELLOW}This will start: MLFlow, MinIO, Redis (ML), Celery workers${NC}"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd quant/infrastructure/docker
    docker-compose -f docker-compose-ml.yml up -d
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ML services started${NC}"
    else
        echo -e "${RED}✗ Failed to start ML services${NC}"
        exit 1
    fi
    cd ../../..
fi

# Step 5: Wait for services to be ready
echo -e "${GREEN}Step 5: Waiting for services to be ready...${NC}"
echo "Waiting for MLFlow..."
for i in {1..30}; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ MLFlow is ready${NC}"
        break
    fi
    sleep 2
    echo -n "."
done
echo ""

echo "Waiting for MinIO..."
for i in {1..30}; do
    if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
        echo -e "${GREEN}✓ MinIO is ready${NC}"
        break
    fi
    sleep 2
    echo -n "."
done
echo ""

# Step 6: Create initial MLFlow experiment
echo -e "${GREEN}Step 6: Setting up MLFlow experiment...${NC}"
cd quant/backend
python << EOF
import mlflow
mlflow.set_tracking_uri("http://localhost:5000")
try:
    mlflow.create_experiment(
        "politician-trade-prediction",
        artifact_location="s3://mlflow-artifacts"
    )
    print("✓ MLFlow experiment created")
except Exception as e:
    print(f"Experiment may already exist: {e}")
EOF
cd ../..

# Step 7: Run a test to verify setup
echo -e "${GREEN}Step 7: Running verification test...${NC}"
cd quant/backend
python << EOF
try:
    # Test imports
    import mlflow
    import torch
    import sklearn
    import networkx
    import statsmodels

    print("✓ All ML libraries imported successfully")

    # Test MLFlow connection
    mlflow.set_tracking_uri("http://localhost:5000")
    experiments = mlflow.search_experiments()
    print(f"✓ Connected to MLFlow ({len(experiments)} experiments)")

    # Test Redis connection
    import redis
    r = redis.Redis(host='localhost', port=6380, db=0)
    r.ping()
    print("✓ Connected to Redis")

    print("\n" + "="*50)
    print("ML Infrastructure Setup Complete! ✓")
    print("="*50)

except Exception as e:
    print(f"✗ Verification failed: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}==================================="
    echo "Setup Complete!"
    echo "===================================${NC}"
    echo ""
    echo "Services running:"
    echo "  - MLFlow UI:      http://localhost:5000"
    echo "  - MinIO Console:  http://localhost:9001"
    echo "  - Flower (Celery): http://localhost:5555"
    echo "  - Redis ML:       localhost:6380"
    echo ""
    echo "Next steps:"
    echo "  1. Access MLFlow UI at http://localhost:5000"
    echo "  2. Start training models: python -m app.cli ml train"
    echo "  3. Check Celery workers: docker logs quant-celery-ml"
    echo ""
    echo "For more information, see:"
    echo "  - ADVANCED_AI_SYSTEM.md"
    echo "  - quant/backend/app/ml/README.md"
    echo ""
else
    echo -e "${RED}Setup failed. Please check the errors above.${NC}"
    exit 1
fi
