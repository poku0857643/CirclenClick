# CircleNClick Quick Start Guide

**Your system is running! Follow these steps to start verifying content.**

## Current Status ✅

- ✅ FastAPI backend: **RUNNING** on http://localhost:8080
- ✅ Extension built: **READY** at `extension/dist/`
- ✅ Native messaging: **INSTALLED**
- ✅ Icons: **GENERATED**

## Step 1: Load Extension in Chrome (2 minutes)

### A. Open Chrome Extensions

1. Open Chrome browser
2. Navigate to: `chrome://extensions/`
3. Enable "Developer mode" (toggle in top-right corner)

### B. Load the Extension

1. Click **"Load unpacked"** button
2. Navigate to: `/Users/eshan/PycharmProjects/circlenclick/extension/dist`
3. Select the `dist` folder and click "Select"

### C. Get Extension ID

After loading, you'll see the extension card. Look for the **Extension ID** (it looks like: `abcdefghijklmnopqrstuvwxyz123456`)

**Copy this ID!** You'll need it for the next step.

### D. Update Native Messaging Manifest

Run this command, replacing `YOUR_EXTENSION_ID` with the actual ID from step C:

```bash
cd /Users/eshan/PycharmProjects/circlenclick

python -c "
import json
manifest_path = '/Users/eshan/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.anthropic.circlenclick.json'
with open(manifest_path, 'r') as f:
    manifest = json.load(f)
manifest['allowed_origins'] = ['chrome-extension://YOUR_EXTENSION_ID/']
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)
print('✅ Updated manifest with extension ID')
"
```

**OR** use the helper script:

```bash
python scripts/update_extension_id.py YOUR_EXTENSION_ID
```

### E. Reload Extension

After updating the manifest:
1. Go back to `chrome://extensions/`
2. Click the **reload icon** on the CircleNClick extension card

## Step 2: Test the Extension (3 minutes)

### A. Check Extension Status

1. Click the **CircleNClick icon** in Chrome toolbar (you may need to pin it)
2. The popup should open
3. Check the **Status tab**:
   - Backend Status should show **"Online"** (green badge)
   - Cloud APIs: "Disabled" (expected - no API keys yet)
   - Cache: Should show some items

### B. Navigate to a Supported Platform

Open one of these sites in a new tab:
- **Facebook**: https://facebook.com
- **X/Twitter**: https://x.com or https://twitter.com
- **Threads**: https://threads.net

### C. Activate Circle & Click

**Method 1 - Extension Icon:**
1. Click the CircleNClick icon
2. Click **"Activate Circle & Click"** button
3. The popup will close

**Method 2 - Keyboard Shortcut:**
1. Press `Ctrl+Shift+C` (Mac: `Cmd+Shift+C`)

### D. Select Content

You should see:
- ✅ Cursor changes to **crosshair**
- ✅ Instruction tooltip appears at top: "Click and drag to select content • Press ESC to cancel"

Now:
1. **Click and hold** on a post or text
2. **Drag** to create a selection box (blue border)
3. **Release** to submit for verification

### E. View Results

After 2-8 seconds, you should see:
- ✅ Beautiful overlay appears near the selected content
- ✅ Verdict displayed (TRUE/FALSE/MISLEADING/UNVERIFIABLE)
- ✅ Confidence percentage with colored bar
- ✅ Explanation text
- ✅ Evidence and sources (if available)

The overlay will auto-dismiss after 15 seconds, or click the **X** to close it.

## Step 3: Test Some Claims

Try verifying these examples:

### Example 1: Known False Claim
Go to any social media post and select this text (or type it in a test post):
```
"The Earth is flat"
```

**Expected Result**:
- Verdict: **FALSE** (red)
- Confidence: ~95%
- Explanation: "This claim has been repeatedly debunked..."

### Example 2: Factual Statement
Select:
```
"Water boils at 100 degrees Celsius at sea level"
```

**Expected Result**:
- Verdict: **TRUE** (green)
- Confidence: High

### Example 3: Opinion (Not a Claim)
Select:
```
"Pizza is the best food"
```

**Expected Result**:
- Verdict: **UNVERIFIABLE** (gray)
- Explanation: This is an opinion, not a factual claim

## Step 4: Check History

1. Click the CircleNClick icon
2. Go to **History** tab
3. See your recent verifications with:
   - Verdict badges
   - Text snippets
   - Timestamps

## Troubleshooting

### Extension Icon Not Showing Results

**Check 1: Backend Running**
```bash
curl http://localhost:8080/health
```
Should return: `{"status":"healthy",...}`

**Check 2: Console Errors**
1. Right-click on the page
2. Select "Inspect"
3. Go to "Console" tab
4. Look for errors starting with `[Content]` or `[Background]`

**Check 3: Native Messaging**
1. Go to `chrome://extensions/`
2. Find CircleNClick
3. Click "Inspect views: background page"
4. Check console for connection errors

### Extension Not Loading

**Solution**: Make sure you selected the `dist` folder, not the `extension` folder.

Correct path: `/Users/eshan/PycharmProjects/circlenclick/extension/dist`

### Selection Not Working

**Try**:
1. Press ESC to cancel
2. Reload the page (Ctrl+R / Cmd+R)
3. Activate Circle & Click again

### Native Messaging Errors

**Fix**:
1. Verify manifest exists:
```bash
cat ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.circlenclick.json
```

2. Verify extension ID is correct
3. Reload extension after updating manifest

## Advanced Testing

### Test with Cloud APIs (Optional)

If you have API keys:

1. Create `.env` file:
```bash
cp .env.example .env
```

2. Add your API keys to `.env`:
```bash
GOOGLE_FACTCHECK_API_KEY=your_key_here
CLAIMBUSTER_API_KEY=your_key_here
FACTIVERSE_API_KEY=your_key_here
```

3. Restart backend:
```bash
pkill -f uvicorn
python -m uvicorn api.app:app --host localhost --port 8080
```

4. Test verification - results will be more accurate!

### Test Different Strategies

In the extension popup:
1. Go to **Settings** tab
2. Change "Verification Strategy":
   - **Hybrid** (recommended): Uses both local + cloud
   - **Local Only**: Fast, offline-capable
   - **Cloud Only**: Most thorough (requires API keys)
3. Click "Save Settings"

## What to Test

### On Facebook
- Select a news headline from a post
- Select a comment with a claim
- Select a shared article title

### On X/Twitter
- Select tweet text with a claim
- Select a thread reply
- Select quoted tweet content

### On Threads
- Select a thread post
- Select a reply

## Next Steps

### 1. Add API Keys (Recommended)
Get free API keys from:
- Google Fact Check: https://developers.google.com/fact-check/tools/api
- ClaimBuster: https://idir.uta.edu/claimbuster/

### 2. Test on Real Posts
Find viral posts or trending claims and verify them!

### 3. Provide Feedback
Found a bug? Have suggestions?
- Check console logs
- Note the content you selected
- Report issues

## System Commands

### Start Backend
```bash
cd /Users/eshan/PycharmProjects/circlenclick
python -m uvicorn api.app:app --host localhost --port 8080
```

### Check Backend Status
```bash
curl http://localhost:8080/health
```

### Rebuild Extension
```bash
cd extension
npm run build
```

### View Logs
Backend logs are in terminal where you started uvicorn.

Extension logs:
- Content script: Right-click page → Inspect → Console
- Background worker: chrome://extensions/ → CircleNClick → "Inspect views"

## Success Indicators

You know it's working when:
- ✅ Extension icon appears in Chrome toolbar
- ✅ Status tab shows "Online" backend
- ✅ Crosshair cursor appears on activation
- ✅ Selection box draws smoothly
- ✅ Results overlay appears after selection
- ✅ History tab shows your verifications

## Need Help?

**Backend not starting?**
```bash
# Check if port 8080 is already in use
lsof -i :8080

# Kill existing process if needed
pkill -f uvicorn
```

**Extension errors?**
- Check Chrome console (F12)
- Verify extension ID in manifest
- Reload extension after any changes

**Still stuck?**
Check the detailed documentation:
- `README.md` - Overall project guide
- `extension/README.md` - Extension-specific docs
- `PHASE4_COMPLETE.md` - Technical details
- `LOCAL_TEST_REPORT.md` - Test results

---

**You're all set!** The system is running. Load the extension and start verifying content! 🚀
