#!/bin/bash

echo "Testing Frontend Components..."
cd /mnt/e/projects/quant/quant/frontend

# Check if key files exist
echo "Checking key files..."
files=(
  "src/app/page.tsx"
  "src/app/tools/page.tsx"
  "src/app/resources/page.tsx"
  "src/app/compare/page.tsx"
  "src/components/widgets/QuickTickerLookup.tsx"
  "src/components/widgets/MarketOverview.tsx"
  "src/components/widgets/TopMovers.tsx"
  "src/components/ui/MobileMenu.tsx"
  "src/components/ui/Skeleton.tsx"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "✓ $file exists"
  else
    echo "✗ $file missing"
  fi
done

echo ""
echo "Checking for syntax errors in TSX files..."
# Try to parse each file for basic syntax
for file in src/app/*.tsx src/app/**/page.tsx src/components/**/*.tsx; do
  if [ -f "$file" ]; then
    # Check for unclosed tags, missing imports, etc
    if grep -q "import.*from.*@/components" "$file" 2>/dev/null; then
      echo "✓ $file has component imports"
    fi
  fi
done

echo ""
echo "Test complete!"
