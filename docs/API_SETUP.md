# Cloud API Setup Guide

This guide explains how to obtain and configure API keys for cloud fact-checking services to enable broader claim verification coverage beyond the local database.

---

## 🌐 Available Cloud APIs

CircleNClick integrates with three fact-checking APIs:

1. **Google Fact Check Tools API** ⭐ RECOMMENDED
   - Coverage: Thousands of fact-checks from 100+ fact-checking organizations
   - Cost: FREE (with generous quota)
   - Best for: Recent news, politics, health claims

2. **ClaimBuster API**
   - Coverage: Academic-grade claim detection and scoring
   - Cost: FREE tier available
   - Best for: Check-worthiness scoring, claim detection

3. **Factiverse API**
   - Coverage: Real-time fact extraction with 220M+ scientific articles
   - Cost: Paid service
   - Best for: Scientific claims, research verification

---

## ✅ Google Fact Check Tools API (Recommended)

### Step 1: Get an API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Create a new project or select an existing one:
   - Click "Select a project" dropdown
   - Click "New Project"
   - Name it "CircleNClick" or similar
   - Click "Create"

3. Enable the Fact Check Tools API:
   - Go to [API Library](https://console.cloud.google.com/apis/library)
   - Search for "Fact Check Tools API"
   - Click on "Fact Check Tools API"
   - Click "ENABLE"

4. Create API credentials:
   - Go to [Credentials](https://console.cloud.google.com/apis/credentials)
   - Click "+ CREATE CREDENTIALS"
   - Select "API key"
   - Copy the generated API key
   - (Optional) Click "Edit API key" to restrict it to Fact Check API only

### Step 2: Add to Environment

Add the API key to your `.env` file:

```bash
# Google Fact Check API
GOOGLE_FACTCHECK_API_KEY=YOUR_API_KEY_HERE
```

### Step 3: Test the Integration

```bash
# Test with CLI
python cli.py verify "Donald Trump won the 2020 election" --strategy cloud

# Or test with API
curl -X POST http://localhost:8080/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"text":"COVID vaccines contain microchips","strategy":"cloud"}'
```

### API Limits

- **Free Tier**: 10,000 requests/day
- **Rate Limit**: 100 requests/100 seconds
- No credit card required

**Documentation**: https://developers.google.com/fact-check/tools/api

---

## 🎓 ClaimBuster API

### Step 1: Register for API Access

1. Go to [ClaimBuster Website](https://idir.uta.edu/claimbuster/)

2. Navigate to the API section

3. Register for a free API key:
   - Fill out the registration form
   - Provide: Name, Email, Institution/Organization
   - Purpose: Research/Development
   - You'll receive an API key via email

### Step 2: Add to Environment

```bash
# ClaimBuster API
CLAIMBUSTER_API_KEY=YOUR_API_KEY_HERE
```

### Step 3: Test the Integration

```bash
python cli.py verify "Climate change is a hoax" --strategy cloud
```

### API Limits

- **Free Tier**: 1,000 requests/day
- Best for research and development

**Documentation**: https://idir.uta.edu/claimbuster/api/

---

## 🔬 Factiverse API

### Step 1: Get API Access

1. Go to [Factiverse Website](https://www.factiverse.ai/)

2. Click "Contact" or "Get Access"

3. Request API credentials:
   - Describe your use case
   - Request pricing information
   - They'll provide API credentials

### Step 2: Add to Environment

```bash
# Factiverse API
FACTIVERSE_API_KEY=YOUR_API_KEY_HERE
FACTIVERSE_API_URL=https://api.factiverse.ai/v1  # Or provided URL
```

### Step 3: Test the Integration

```bash
python cli.py verify "Hydroxychloroquine cures COVID-19" --strategy cloud
```

### API Limits

- Paid service with custom pricing
- Contact Factiverse for quotas

**Website**: https://www.factiverse.ai/

---

## 🧪 Testing Your Setup

### Check API Configuration

```bash
# Check which APIs are configured
python cli.py status

# Or use the API health endpoint
curl http://localhost:8080/health
```

### Test Each API Individually

```python
# test_cloud_apis.py
import asyncio
from cloud.google_factcheck import GoogleFactCheckClient

async def test_google():
    client = GoogleFactCheckClient()
    if not client.is_configured:
        print("❌ Google API not configured")
        return

    result = await client.verify_claim("The Earth is flat")
    if result:
        print(f"✅ Google API working: {result.rating}")
    else:
        print("❌ No results from Google API")

asyncio.run(test_google())
```

### Test Full Verification Flow

```bash
# Create test file
cat > test_claims.txt << EOF
The Earth is flat
Vaccines cause autism
Climate change is caused by human activity
5G towers spread COVID-19
EOF

# Verify each claim
while read claim; do
    echo "Testing: $claim"
    python cli.py verify "$claim" --strategy hybrid
    echo "---"
done < test_claims.txt
```

---

## 📊 Verification Strategies

Configure which verification method to use:

### 1. Local Only (Default)
- Uses semantic similarity with local claims database
- **Fastest**: < 1 second
- **Coverage**: ~14 known claims + semantic matching
- **Cost**: $0
```bash
python cli.py verify "claim" --strategy local
```

### 2. Cloud Only
- Uses external fact-checking APIs
- **Speed**: 2-8 seconds
- **Coverage**: Millions of claims
- **Cost**: Free tier limits apply
```bash
python cli.py verify "claim" --strategy cloud
```

### 3. Hybrid (Recommended)
- Tries local first, falls back to cloud if low confidence
- **Speed**: 1-8 seconds (adaptive)
- **Coverage**: Best of both
- **Cost**: Minimal (only calls cloud when needed)
```bash
python cli.py verify "claim" --strategy hybrid
```

---

## 🔐 Security Best Practices

1. **Never commit API keys to git**
   - Add `.env` to `.gitignore`
   - Use `.env.example` for templates

2. **Restrict API keys**
   - Use Google Cloud Console to restrict keys to specific APIs
   - Set HTTP referrer restrictions if using from browser

3. **Rotate keys regularly**
   - Generate new keys every 90 days
   - Revoke old keys immediately

4. **Monitor usage**
   - Check Google Cloud Console for API usage
   - Set up billing alerts

---

## 🚨 Troubleshooting

### "API key not configured"
```bash
# Check your .env file exists
ls -la .env

# Verify it contains the key
cat .env | grep GOOGLE_FACTCHECK_API_KEY

# Make sure backend is restarted
./start.sh
```

### "403 Forbidden" or "401 Unauthorized"
- Double-check your API key is correct
- Ensure the API is enabled in Google Cloud Console
- Check if you've exceeded quota

### "No results found"
- Some claims may not have fact-checks available
- Try rephrasing the claim
- Use hybrid mode to fall back to local database

### "Timeout" or "Connection Error"
- Check your internet connection
- Cloud APIs may be temporarily unavailable
- Increase timeout in `.env`:
  ```bash
  CLOUD_TIMEOUT_SECONDS=30
  ```

---

## 📈 Next Steps

Once you have APIs configured:

1. **Test with real claims**: Try current news headlines
2. **Expand coverage**: The more APIs you enable, the better
3. **Monitor performance**: Check logs in `logs/` directory
4. **Contribute**: Help expand the local claims database

---

## 💡 Tips for Best Results

1. **Use hybrid mode**: Best balance of speed and coverage
2. **Clear cache occasionally**: `rm -rf cache/*` to get fresh results
3. **Check logs**: `tail -f logs/circlenclick.log` for debugging
4. **Rate limiting**: Don't exceed API quotas
5. **Quality over quantity**: One good API (Google) is better than multiple bad ones

---

## 📚 Additional Resources

- [Google Fact Check Tools Documentation](https://developers.google.com/fact-check/tools/api)
- [ClaimBuster Research Papers](https://idir.uta.edu/claimbuster/publications/)
- [Factiverse Blog](https://www.factiverse.ai/blog)
- [CircleNClick GitHub](https://github.com/poku0857643/CirclenClick)

---

**Need help?** Open an issue on [GitHub](https://github.com/poku0857643/CirclenClick/issues)
