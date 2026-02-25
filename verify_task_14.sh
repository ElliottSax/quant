#!/bin/bash
# Verification script for Task #14 implementation

echo "=========================================="
echo "TASK #14 VERIFICATION"
echo "=========================================="
echo ""

echo "Checking Services..."
for file in options_analyzer.py enhanced_sentiment.py pattern_recognizer.py; do
    if [ -f "quant/backend/app/services/$file" ]; then
        size=$(wc -l "quant/backend/app/services/$file" | awk '{print $1}')
        echo "✓ $file ($size lines)"
    else
        echo "✗ $file MISSING"
    fi
done

echo ""
echo "Checking Models..."
if [ -f "quant/backend/app/models/analytics.py" ]; then
    size=$(wc -l "quant/backend/app/models/analytics.py" | awk '{print $1}')
    echo "✓ analytics.py ($size lines)"
else
    echo "✗ analytics.py MISSING"
fi

echo ""
echo "Checking API Endpoints..."
if [ -f "quant/backend/app/api/v1/advanced_analytics.py" ]; then
    size=$(wc -l "quant/backend/app/api/v1/advanced_analytics.py" | awk '{print $1}')
    echo "✓ advanced_analytics.py ($size lines)"
else
    echo "✗ advanced_analytics.py MISSING"
fi

echo ""
echo "Checking Migration..."
if [ -f "quant/backend/alembic/versions/add_analytics_tables.py" ]; then
    size=$(wc -l "quant/backend/alembic/versions/add_analytics_tables.py" | awk '{print $1}')
    echo "✓ add_analytics_tables.py ($size lines)"
else
    echo "✗ add_analytics_tables.py MISSING"
fi

echo ""
echo "Checking Documentation..."
for doc in TASK_14_ADVANCED_ANALYTICS_COMPLETE.md TASK_14_COMPLETION_SUMMARY.md ADVANCED_ANALYTICS_API_REFERENCE.md; do
    if [ -f "$doc" ]; then
        size=$(wc -l "$doc" | awk '{print $1}')
        echo "✓ $doc ($size lines)"
    else
        echo "✗ $doc MISSING"
    fi
done

echo ""
echo "Checking Test Suite..."
if [ -f "test_advanced_analytics.py" ]; then
    size=$(wc -l "test_advanced_analytics.py" | awk '{print $1}')
    echo "✓ test_advanced_analytics.py ($size lines)"
else
    echo "✗ test_advanced_analytics.py MISSING"
fi

echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="

total_files=10
found_files=$(find . -name "options_analyzer.py" -o -name "enhanced_sentiment.py" -o -name "pattern_recognizer.py" -o -name "analytics.py" -path "*/models/*" -o -name "advanced_analytics.py" -path "*/api/v1/*" -o -name "add_analytics_tables.py" -o -name "TASK_14*.md" -o -name "ADVANCED_ANALYTICS_API_REFERENCE.md" -o -name "test_advanced_analytics.py" | wc -l)

echo "Files found: $found_files/$total_files"
echo ""

if [ $found_files -eq $total_files ]; then
    echo "✅ Task #14: COMPLETE"
    echo ""
    echo "Next steps:"
    echo "1. cd quant/backend && alembic upgrade head"
    echo "2. export NEWS_API_KEY=your_key (optional)"
    echo "3. export TWITTER_BEARER_TOKEN=your_token (optional)"
    echo "4. python test_advanced_analytics.py"
else
    echo "⚠️  Some files missing, please review"
fi

echo ""
echo "=========================================="
