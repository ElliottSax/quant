#!/bin/bash
# Programmatic Render deployment via API

# Render API endpoint
RENDER_SERVICE_ID="exs-d6fllop5pdvs738rgc90"  # From your blueprint
RENDER_API_URL="https://api.render.com/v1/services/${RENDER_SERVICE_ID}/deploys"

echo "🚀 Triggering Render Deployment Programmatically"
echo "=================================================="
echo ""

# Check if RENDER_API_KEY is set
if [ -z "$RENDER_API_KEY" ]; then
    echo "⚠️  RENDER_API_KEY not found in environment"
    echo ""
    echo "To get your API key:"
    echo "1. Go to: https://dashboard.render.com/account/api-keys"
    echo "2. Click 'Create API Key'"
    echo "3. Copy the key"
    echo "4. Run: export RENDER_API_KEY='your_key_here'"
    echo "5. Run this script again"
    echo ""
    echo "Or run directly:"
    echo "RENDER_API_KEY='your_key' bash deploy_render.sh"
    exit 1
fi

echo "📡 Triggering deploy via Render API..."
echo "Service ID: ${RENDER_SERVICE_ID}"
echo ""

# Trigger deploy
RESPONSE=$(curl -s -X POST \
  "${RENDER_API_URL}" \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "clearCache": "clear"
  }')

# Check response
if echo "$RESPONSE" | grep -q "id"; then
    DEPLOY_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "✅ Deploy triggered successfully!"
    echo "Deploy ID: ${DEPLOY_ID}"
    echo ""
    echo "Monitor progress at:"
    echo "https://dashboard.render.com/web/${RENDER_SERVICE_ID}"
else
    echo "❌ Deploy failed. Response:"
    echo "$RESPONSE"
    exit 1
fi

echo ""
echo "🔍 Checking deploy status..."
sleep 5

STATUS_URL="https://api.render.com/v1/services/${RENDER_SERVICE_ID}"
STATUS=$(curl -s "${STATUS_URL}" \
  -H "Authorization: Bearer ${RENDER_API_KEY}")

if echo "$STATUS" | grep -q "live"; then
    SERVICE_URL=$(echo "$STATUS" | grep -o '"serviceUrl":"[^"]*"' | cut -d'"' -f4)
    echo ""
    echo "✅ Service URL: ${SERVICE_URL}"
    echo ""
    echo "Test endpoints:"
    echo "  Health: ${SERVICE_URL}/health"
    echo "  Docs: ${SERVICE_URL}/docs"
    echo "  Finnhub: ${SERVICE_URL}/api/v1/finnhub/demo/quote/AAPL"
fi

echo ""
echo "=================================================="
echo "✅ Deployment triggered!"
echo "Check dashboard for build progress."
echo "=================================================="
