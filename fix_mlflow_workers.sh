#!/bin/bash

# Fix MLFlow Worker OOM Issues

echo "=========================================="
echo " Fixing MLFlow Worker Configuration"
echo "=========================================="
echo ""

cd /mnt/e/projects/quant/quant/infrastructure/docker

echo "1. Stopping MLFlow..."
docker-compose -f docker-compose-ml.yml stop mlflow

echo ""
echo "2. Removing old MLFlow container..."
docker rm quant-mlflow 2>/dev/null || true

echo ""
echo "3. Starting MLFlow with optimized settings..."
docker-compose -f docker-compose-ml.yml up -d mlflow

echo ""
echo "4. Waiting for MLFlow to start..."
sleep 10

echo ""
echo "5. Checking MLFlow status..."
if docker ps | grep -q quant-mlflow; then
    echo "  ✓ MLFlow is running"

    echo ""
    echo "6. Testing MLFlow..."
    if curl -sf http://localhost:5000/health > /dev/null; then
        echo "  ✓ MLFlow health check passed"
    else
        echo "  ⚠  MLFlow may still be starting..."
    fi

    echo ""
    echo "7. Checking worker status..."
    docker logs quant-mlflow --tail 10
else
    echo "  ❌ MLFlow failed to start"
    echo ""
    echo "Logs:"
    docker logs quant-mlflow --tail 20
    exit 1
fi

echo ""
echo "=========================================="
echo " MLFlow Worker Fix Complete"
echo "=========================================="
echo ""
echo "Access MLFlow UI at: http://localhost:5000"
