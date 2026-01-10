# CircleNClick Browser Extension

The browser extension component of CircleNClick that enables "Circle & Click" content verification on Facebook, X (Twitter), and Threads.

## Features

- **Circle & Click Selection**: Visual selection interface to choose content
- **Native Messaging**: Communicates with Python backend via native messaging protocol
- **Platform Adapters**: Specialized extraction for Facebook, X, and Threads
- **Beautiful Results**: In-page overlay showing verification results
- **Keyboard Shortcut**: `Ctrl+Shift+C` (or `Cmd+Shift+C` on Mac)
- **History & Settings**: Popup UI for configuration and verification history

## Development Setup

### Prerequisites

- Node.js 18+ and npm
- Python backend running (see main README)
- Native messaging host installed

### Installation

```bash
cd extension
npm install
```

### Build

```bash
# Development build with watch mode
npm run dev

# Production build
npm run build
```

The compiled extension will be in the `dist/` directory.

### Load in Browser

#### Chrome/Edge
1. Navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension/dist` directory

#### Firefox
1. Navigate to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select any file in the `extension/dist` directory

## Project Structure

```
extension/
├── src/
│   ├── background/          # Background service worker
│   │   └── index.ts         # Native messaging client
│   ├── content/             # Content scripts
│   │   ├── index.ts         # Main content script
│   │   ├── selection-overlay.ts   # Circle & Click UI
│   │   ├── result-overlay.ts      # Results display
│   │   ├── platform-adapters/     # Platform-specific extractors
│   │   │   ├── facebook.ts
│   │   │   ├── x.ts
│   │   │   └── threads.ts
│   │   ├── content.css      # Content script styles
│   │   └── overlay.html     # Overlay template
│   └── popup/               # Extension popup
│       ├── popup.html       # Popup UI
│       └── index.ts         # Popup logic
├── icons/                   # Extension icons (16, 48, 128)
├── manifest.json            # Extension manifest (v3)
├── package.json             # npm dependencies
├── tsconfig.json            # TypeScript config
└── webpack.config.js        # Build configuration
```

## Usage

### Activating Verification

1. **Click Extension Icon**: Opens popup, click "Activate Circle & Click"
2. **Keyboard Shortcut**: Press `Ctrl+Shift+C` (or `Cmd+Shift+C`)
3. **Auto-activate**: Enable in settings for automatic activation on supported sites

### Verifying Content

1. Activate verification mode (cursor changes to crosshair)
2. Click and drag to select text or post
3. Release to submit for verification
4. Wait 2-8 seconds for results
5. View verdict overlay with confidence, evidence, and sources
6. Press ESC to cancel selection

### Settings

- **Verification Strategy**: Choose local, cloud, or hybrid verification
- **Auto-activate**: Automatically enable on supported platforms
- **Cache**: Clear cached verification results

### History

View past verification requests with:
- Verdict and confidence score
- Original text snippet
- Timestamp

## Architecture

### Communication Flow

```
Content Script (selection)
    ↓ chrome.runtime.sendMessage
Background Worker (native messaging)
    ↓ stdin/stdout
Python Native Host
    ↓ HTTP/FastAPI
Verification Engine
    ↓
Results returned back through chain
```

### Native Messaging Protocol

Messages follow JSON format:

**Request:**
```json
{
  "type": "VERIFY",
  "request_id": "unique_id",
  "data": {
    "text": "Content to verify",
    "url": "https://platform.com/post/123",
    "platform": "facebook",
    "author": "John Doe",
    "strategy": "hybrid"
  }
}
```

**Response:**
```json
{
  "type": "RESPONSE",
  "request_id": "unique_id",
  "data": {
    "verdict": "FALSE",
    "confidence": 87,
    "explanation": "...",
    "sources": ["..."],
    "evidence": ["..."]
  }
}
```

## Platform Adapters

Each platform has a specialized adapter that extracts:
- Author name
- Post URL
- Timestamp
- Post container element

Platform-specific DOM selectors are used to reliably find this information despite frequent UI changes.

## Development

### Testing

1. Start Python backend: `uvicorn api.app:app --port 8080`
2. Build extension: `npm run dev`
3. Load in browser (see above)
4. Navigate to Facebook/X/Threads
5. Activate and test selection

### Debugging

- **Background Worker**: `chrome://extensions/` → Inspect service worker
- **Content Script**: Right-click page → Inspect → Console
- **Native Messaging**: Check logs at `native_messaging/logs/`
- **Network**: Check Python backend logs

### Common Issues

1. **Native messaging not working**
   - Ensure manifests are installed: `python scripts/setup_native_host.py`
   - Check Chrome manifest at: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/` (macOS)
   - Verify Python backend is running

2. **Selection not working**
   - Check content script loaded in page inspector
   - Verify manifest permissions for the platform
   - Check console for errors

3. **Results not showing**
   - Ensure backend is reachable
   - Check background worker logs
   - Verify native host connection

## Contributing

When modifying the extension:

1. Follow TypeScript best practices
2. Test on all supported platforms (Facebook, X, Threads)
3. Verify Chrome and Firefox compatibility
4. Update manifest version when releasing
5. Rebuild before testing: `npm run build`

## Packaging for Distribution

### Chrome Web Store

```bash
# Build production version
npm run build

# Create ZIP
cd dist && zip -r ../circlenclick-extension.zip . && cd ..
```

Upload to Chrome Web Store Developer Dashboard.

### Firefox Add-ons

```bash
# Build production version
npm run build

# Create signed XPI
web-ext sign --source-dir dist
```

## License

MIT License - see main project LICENSE file
