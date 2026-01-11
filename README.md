# CircleNClick

> Web as canvas - Circle & Click to verify any content you want

CircleNClick is a content verification tool that helps you identify misinformation, fake news, and AI-generated content on social media platforms like Facebook, X (Twitter), and Threads. Simply select content on the page and get instant verification results.

## Features

- **🎯 Misinformation Detection**: Check if claims are true, false, or misleading
- **🤖 ML-Powered Semantic Matching**: Detects claim variations using sentence transformers
- **💨 Blazing Fast Local Verification**: <1s response with 14-claim database + semantic matching
- **☁️ Cloud API Integration**: Access millions of fact-checks from Google, ClaimBuster, Factiverse
- **🔄 Hybrid Verification**: Combines fast local models with comprehensive cloud APIs
- **🌐 Multi-Platform Support**: Works on Facebook, X (Twitter), and Threads
- **🔐 Privacy-First**: Local models process sensitive content on your device
- **📚 Educational Responses**: Detailed explanations with evidence and authoritative sources

## Project Status

✅ **Phase 1 Complete**: CLI Development Tool
- Core verification engine implemented
- Local content processing and claim extraction
- CLI interface for testing

✅ **Phase 2 Complete**: Cloud API Integration
- Google Fact Check API integration
- ClaimBuster API integration
- Factiverse API integration
- Multi-source result aggregation
- Disk-based caching layer (24h TTL)
- Parallel API calls for speed

✅ **Phase 3 Complete**: Native Messaging Bridge & API
- Native messaging protocol (Chrome/Firefox)
- Native messaging host for extension communication
- FastAPI REST API server
- Verification endpoints with auto-docs
- Installation scripts and manifest generator

✅ **Phase 4 Complete**: Browser Extension
- Circle & Click visual selection interface
- Content scripts for Facebook, X, and Threads
- Background service worker with native messaging
- Beautiful result overlays with verdict visualization
- Popup UI with settings and history
- TypeScript + Webpack build system
- Extension icons and full packaging

📝 **Next Phases**:
- Phase 5: MCP integration for LLM-powered fact-checking
- Phase 6: Chrome Web Store and Firefox Add-ons distribution

## Installation

### Prerequisites
- Python 3.12+
- pip or poetry

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/circlenclick.git
cd circlenclick
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (optional for cloud APIs):
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Install native messaging host (required for browser extension):
```bash
python scripts/setup_native_host.py
```

### Browser Extension Setup

1. Build the extension:
```bash
cd extension
npm install
npm run build
```

2. Load in Chrome:
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select `extension/dist/` directory

3. Load in Firefox:
   - Navigate to `about:debugging#/runtime/this-firefox`
   - Click "Load Temporary Add-on"
   - Select any file in `extension/dist/`

### Cloud API Setup (Optional but Recommended)

CircleNClick works offline with local database + ML semantic matching. For broader coverage of millions of claims, enable cloud APIs:

1. **Get API Keys** (all have free tiers):
   - [Google Fact Check API](https://console.cloud.google.com/) - **RECOMMENDED** (10,000 free requests/day)
   - [ClaimBuster API](https://idir.uta.edu/claimbuster/) - Academic fact-checking (1,000 free/day)
   - [Factiverse API](https://www.factiverse.ai/) - Scientific claim verification (paid)

2. **Configure**:
   ```bash
   # Copy template
   cp .env.example .env

   # Add your keys
   nano .env  # or use any text editor
   ```

3. **Test**:
   ```bash
   python scripts/test_cloud_apis.py
   ```

**See [docs/API_SETUP.md](docs/API_SETUP.md) for detailed setup instructions.**

## Usage

### Browser Extension (Circle & Click)

1. **Activate**: Click extension icon or press `Ctrl+Shift+C` (Mac: `Cmd+Shift+C`)
2. **Select**: Click and drag to select content on Facebook, X, or Threads
3. **Verify**: Release to submit for verification
4. **Results**: View verdict overlay with confidence, evidence, and sources

**Supported Platforms**:
- Facebook (facebook.com)
- X / Twitter (x.com, twitter.com)
- Threads (threads.net)

### CLI Commands

#### Verify Content

```bash
# Verify a text claim
python cli.py verify "The Earth is flat"

# Verify from file
python cli.py verify --file article.txt

# Specify platform
python cli.py verify "Some claim" --platform twitter

# Choose verification strategy
python cli.py verify "Claim" --strategy local   # Fast, local only
python cli.py verify "Claim" --strategy cloud   # Comprehensive, uses APIs
python cli.py verify "Claim" --strategy hybrid  # Balanced (default)

# Output as JSON
python cli.py verify "Claim" --json
```

#### Check Configuration

```bash
# View current configuration and API key status
python cli.py info
```

#### Run Tests

```bash
# Run quick tests with sample content
python cli.py test
```

### Example Output

```
╔═══════════════════════════════════════════╗
║      CircleNClick Content Verifier       ║
║   Check if content is fake, AI-generated,║
║         or contains misinformation       ║
╚═══════════════════════════════════════════╝

╭────────────── Verdict ──────────────╮
│ ✗ FALSE                             │
╰─────────────────────────────────────╯
╭─────────────────┬────────────╮
│ Confidence      │ 95.0%      │
│ Strategy Used   │ local_only │
│ Processing Time │ 0.00s      │
╰─────────────────┴────────────╯

╭─────────────── Explanation ───────────────╮
│ This claim has been repeatedly debunked   │
│ by scientific evidence.                   │
╰───────────────────────────────────────────╯

Evidence:
  1. Multiple peer-reviewed studies contradict this claim

Sources:
  1. Scientific consensus
```

## Architecture

```
Browser Extension (JavaScript/TypeScript)
         ↓ Native Messaging
Python Native Host + FastAPI Service
         ↓
Verification Engine (Hybrid: Local Models + Cloud APIs)
         ↓
Results displayed in-place on platform
```

### Components

- **CLI** (`cli.py`): Command-line interface for development and testing
- **Core Engine** (`core/`): Main verification logic
  - `verification_engine.py`: Orchestrates the verification process
  - `content_processor.py`: Extracts and preprocesses claims
  - `hybrid_decisor.py`: Decides between local/cloud/hybrid strategies
- **Utils** (`utils/`): Configuration and logging utilities
- **Models** (`model/`): Local ML models for fact-checking (future)
- **Cloud** (`cloud/`): Cloud API integrations (future)
- **Extension** (`extension/`): Browser extension code (future)

## Verification Strategies

### Local Only
- **Speed**: 0.5-2 seconds
- **Accuracy**: Basic claim detection
- **Use Case**: Quick screening, offline verification
- **Privacy**: All processing on device

### Cloud Only
- **Speed**: 5-15 seconds
- **Accuracy**: Comprehensive fact-checking
- **Use Case**: Important claims requiring multiple sources
- **APIs**: Google Fact Check, ClaimBuster, Factiverse, LLMs

### Hybrid (Default)
- **Speed**: 2-8 seconds
- **Accuracy**: Balanced
- **Use Case**: General purpose verification
- **Flow**: Local model → Cloud APIs (if needed) → Aggregated result

## API Keys (Optional)

To enable cloud verification, configure these API keys in `.env`:

- **Google Fact Check Tools API**: [Get Key](https://developers.google.com/fact-check/tools/api)
- **ClaimBuster API**: [Get Key](https://idir.uta.edu/claimbuster/) (free tier available)
- **Factiverse API**: [Get Key](https://www.factiverse.ai/)
- **OpenAI API**: [Get Key](https://platform.openai.com/api-keys) (optional)
- **Anthropic API**: [Get Key](https://console.anthropic.com/) (optional)

## Development

### Project Structure

```
circlenclick/
├── cli.py                  # CLI entry point
├── core/                   # Core verification logic
│   ├── verification_engine.py
│   ├── content_processor.py
│   └── hybrid_decisor.py
├── utils/                  # Utilities
│   ├── config.py
│   └── logger.py
├── model/                  # ML models (future)
├── cloud/                  # Cloud APIs (future)
├── auth/                   # Authentication (future)
├── mcp/                    # MCP integration (future)
├── extension/              # Browser extension (future)
└── requirements.txt        # Python dependencies
```

### Running Tests

```bash
# Run pytest (when tests are added)
pytest tests/

# Run CLI test
python cli.py test
```

## Roadmap

- [x] **Phase 1**: CLI development tool with local verification
- [x] **Phase 2**: Cloud API integration
  - [x] Google Fact Check API
  - [x] ClaimBuster API
  - [x] Factiverse API
  - [x] Result aggregation from multiple sources
  - [x] Caching layer to reduce API costs
  - [ ] LLM integration (OpenAI/Claude) - Optional
- [ ] **Phase 3**: Native messaging bridge
- [ ] **Phase 4**: Browser extension
  - [ ] Content selection UI ("Circle & Click")
  - [ ] Result overlay on platforms
  - [ ] Settings and history
- [ ] **Phase 5**: MCP integration for advanced fact-checking
- [ ] **Phase 6**: Human-in-loop feedback system
- [ ] **Phase 7**: ML model training and optimization

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with FastAPI, transformers, and sentence-transformers
- Fact-checking APIs: Google, ClaimBuster, Factiverse
- Model Context Protocol (MCP) by Anthropic
