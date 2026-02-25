#!/bin/bash
# Monitor Render backend deployment status

echo "🔄 Monitoring Render Backend Deployment"
echo "========================================"
echo ""
echo "Checking every 30 seconds... (Ctrl+C to stop)"
echo ""

# Possible backend URLs
URLS=(
    "https://quant-backend.onrender.com"
    "https://quant-backend-production.onrender.com"
)

CHECK_COUNT=0
MAX_CHECKS=20  # Max 10 minutes

while [ $CHECK_COUNT -lt $MAX_CHECKS ]; do
    CHECK_COUNT=$((CHECK_COUNT + 1))
    TIMESTAMP=$(date '+%H:%M:%S')
    
    echo "[$TIMESTAMP] Check #$CHECK_COUNT - Testing backend URLs..."
    
    FOUND_LIVE=false
    
    for URL in "${URLS[@]}"; do
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$URL/health" 2>&1)
        
        if [ "$RESPONSE" = "200" ]; then
            echo ""
            echo "🎉 =================================="
            echo "✅ BACKEND IS LIVE!"
            echo "===================================="
            echo ""
            echo "Backend URL: $URL"
            echo "Health: $URL/health"
            echo "API Docs: $URL/docs"
            echo "Test Finnhub: $URL/api/v1/finnhub/demo/quote/AAPL"
            echo ""
            echo "Next steps:"
            echo "1. Update Vercel frontend API URL to: $URL/api/v1"
            echo "2. Redeploy frontend: vercel --prod"
            echo "3. Test full stack!"
            echo ""
            FOUND_LIVE=true
            exit 0
        elif [ "$RESPONSE" = "503" ] || [ "$RESPONSE" = "502" ]; then
            echo "  ⏳ $URL - Service starting (HTTP $RESPONSE)..."
        else
            echo "  ⏳ $URL - Not ready (HTTP $RESPONSE)"
        fi
    done
    
    if [ "$FOUND_LIVE" = false ]; then
        if [ $CHECK_COUNT -lt $MAX_CHECKS ]; then
            echo "  💤 Waiting 30 seconds before next check..."
            echo ""
            sleep 30
        fi
    fi
done

echo ""
echo "⏱️  Timeout reached after $MAX_CHECKS checks"
echo "Backend may still be building. Check Render dashboard:"
echo "https://dashboard.render.com/blueprint/exs-d6fllop5pdvs738rgc90"
