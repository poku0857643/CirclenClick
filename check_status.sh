#!/bin/bash
# CircleNClick System Status Check

cd "$(dirname "$0")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CircleNClick System Status Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Backend
echo "🌐 Backend Server"
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "   ✅ Running on http://localhost:8080"
    echo "   Status: $(curl -s http://localhost:8080/health | python -m json.tool 2>/dev/null | grep '"status"' | cut -d':' -f2 | tr -d ' ,"')"
else
    echo "   ❌ Not running"
    echo "   → Start with: ./start.sh"
fi
echo ""

# Check Extension Build
echo "📦 Browser Extension"
if [ -d "extension/dist" ] && [ -f "extension/dist/manifest.json" ]; then
    echo "   ✅ Built and ready"
    echo "   Location: $(pwd)/extension/dist"
    FILE_COUNT=$(ls -1 extension/dist | wc -l | tr -d ' ')
    echo "   Files: $FILE_COUNT"
else
    echo "   ❌ Not built"
    echo "   → Build with: cd extension && npm run build"
fi
echo ""

# Check Extension Icons
echo "🎨 Extension Icons"
if [ -f "extension/dist/icons/icon16.png" ] && \
   [ -f "extension/dist/icons/icon48.png" ] && \
   [ -f "extension/dist/icons/icon128.png" ]; then
    echo "   ✅ All sizes generated"
else
    echo "   ❌ Missing icons"
    echo "   → Generate with: python scripts/generate_extension_icons.py"
fi
echo ""

# Check Native Messaging - Chrome
echo "🔗 Native Messaging (Chrome)"
CHROME_MANIFEST="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.anthropic.circlenclick.json"
if [ -f "$CHROME_MANIFEST" ]; then
    echo "   ✅ Manifest installed"
    EXTENSION_ID=$(cat "$CHROME_MANIFEST" | grep 'chrome-extension' | sed 's/.*chrome-extension:\/\/\([^\/]*\).*/\1/')
    if [ -n "$EXTENSION_ID" ] && [ "$EXTENSION_ID" != "circlenclick@extension.id" ]; then
        echo "   Extension ID: $EXTENSION_ID"
    else
        echo "   ⚠️  Extension ID not configured"
        echo "   → Update with: python scripts/update_extension_id.py YOUR_ID"
    fi
else
    echo "   ❌ Not installed"
    echo "   → Install with: python scripts/setup_native_host.py"
fi
echo ""

# Check Native Messaging - Firefox
echo "🔗 Native Messaging (Firefox)"
FIREFOX_MANIFEST="$HOME/Library/Application Support/Mozilla/NativeMessagingHosts/com.anthropic.circlenclick.json"
if [ -f "$FIREFOX_MANIFEST" ]; then
    echo "   ✅ Manifest installed"
else
    echo "   ❌ Not installed"
    echo "   → Install with: python scripts/setup_native_host.py"
fi
echo ""

# Check Python Environment
echo "🐍 Python Environment"
if [ -d ".venv" ]; then
    echo "   ✅ Virtual environment exists"
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        PYTHON_VERSION=$(python --version 2>&1)
        echo "   $PYTHON_VERSION"
    fi
else
    echo "   ⚠️  No virtual environment"
fi
echo ""

# Check API Keys
echo "🔑 API Keys"
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
    GOOGLE_KEY=$(grep "GOOGLE_FACTCHECK_API_KEY" .env | cut -d'=' -f2 | tr -d ' ')
    CLAIMBUSTER_KEY=$(grep "CLAIMBUSTER_API_KEY" .env | cut -d'=' -f2 | tr -d ' ')

    if [ -n "$GOOGLE_KEY" ] && [ "$GOOGLE_KEY" != "your_key_here" ]; then
        echo "   ✅ Google Fact Check API configured"
    else
        echo "   ⚠️  Google Fact Check API not configured"
    fi

    if [ -n "$CLAIMBUSTER_KEY" ] && [ "$CLAIMBUSTER_KEY" != "your_key_here" ]; then
        echo "   ✅ ClaimBuster API configured"
    else
        echo "   ⚠️  ClaimBuster API not configured"
    fi
else
    echo "   ⚠️  No .env file"
    echo "   → Create with: cp .env.example .env"
fi
echo ""

# Check Cache
echo "💾 Cache"
if [ -d "cache" ]; then
    CACHE_SIZE=$(du -sh cache 2>/dev/null | cut -f1)
    CACHE_FILES=$(find cache -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "   ✅ Cache directory exists"
    echo "   Size: $CACHE_SIZE"
    echo "   Items: $CACHE_FILES"
else
    echo "   ⚠️  Cache not initialized"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Quick Actions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Start Backend:    ./start.sh"
echo "  Build Extension:  cd extension && npm run build"
echo "  Open Guide:       cat QUICKSTART.md"
echo ""
echo "  Load Extension:"
echo "  1. Open Chrome → chrome://extensions/"
echo "  2. Enable Developer mode"
echo "  3. Load unpacked → Select extension/dist/"
echo ""
