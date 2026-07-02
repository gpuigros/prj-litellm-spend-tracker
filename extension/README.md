# LLM Spend Tracker - VS Code Extension

Track and visualize your LLM (Large Language Model) expenditure directly in VS Code.

## Features

- **Status Bar Integration**: Quick glance at current month's LLM spend
- **Rich Sidebar Dashboard**: Comprehensive spend visualization
- **Multiple Views**: Break down spend by model, project, and time period
- **Budget Tracking**: Monitor usage against budget limits with visual warnings
- **Auto-Refresh**: Keep data current with configurable refresh intervals

## Requirements

- VS Code 1.85.0 or higher
- LLM Spend API backend running (see backend/README.md)
- LiteLLM API key

## Installation

1. Build the extension:

   ```bash
   cd extension
   npm install
   npm run package
   ```

2. Install the VSIX file:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Click "..." menu → "Install from VSIX..."
   - Select the generated `.vsix` file

## Configuration

Configure the extension in VS Code settings:

- `llmSpend.apiBaseUrl`: Base URL of the LLM Spend API (default: <http://localhost:8000>)
- `llmSpend.refreshInterval`: Auto-refresh interval in seconds (default: 300, 0 to disable)
- `llmSpend.defaultPeriod`: Default time period (today/week/month, default: month)
- `llmSpend.statusBarFormat`: Status bar display format (default: both)
  - `amount` — shows only the dollar amount (e.g. `$12.34`)
  - `percentage` — shows only the budget percentage (e.g. `45.2%`)
  - `both` — shows amount and percentage (e.g. `$12.34 / 45.2%`)

## Usage

1. **Set API Key**: On first use, you'll be prompted to enter your LiteLLM API key
2. **View Spend**: Click the LLM Spend icon in the activity bar to open the sidebar
3. **Refresh**: Use the refresh command or wait for auto-refresh
4. **Change Period**: Select different time periods in the sidebar

## Commands

- `LLM Spend: Refresh Data` - Manually refresh spend data
- `LLM Spend: Open Sidebar` - Open the spend dashboard
- `LLM Spend: Configure Settings` - Open extension settings

## Development

```bash
# Install dependencies
npm install

# Compile
npm run compile

# Watch mode
npm run watch

# Run tests
npm test

# Lint
npm run lint

# Format
npm run format
```

## Project Structure

```
extension/
├── src/
│   ├── api/              # API client and repositories
│   ├── auth/             # Authentication management
│   ├── cache/            # Caching layer
│   ├── config/           # Configuration management
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── constants.ts      # Constants and configuration keys
│   └── extension.ts      # Extension entry point
├── resources/            # Icons and assets
├── package.json          # Extension manifest
└── tsconfig.json         # TypeScript configuration
```

## License

PolyForm Noncommercial License 1.0.0 - see [LICENSE](../LICENSE) file for details.

This software is free for noncommercial use, including forking, studying, modifying, and contributing via pull requests. Commercial use requires a separate license from the copyright holder.
