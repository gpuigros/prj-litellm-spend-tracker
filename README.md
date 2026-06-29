# LLM Spend Tracker

A complete system for tracking and visualizing LLM (Large Language Model) expenditure in VS Code. This project consists of two main components:

1. **VS Code Extension** (TypeScript) - Client-side UI that displays spend information
2. **Internal Spend API** (Python/FastAPI) - Backend service that aggregates LiteLLM data

## Overview

This system provides developers with real-time insights into their AI-assisted development costs. The VS Code extension displays spend information in both a rich sidebar interface and the status bar, while the Python backend aggregates data from LiteLLM and enforces user-scoped access control.

**Key Architecture Point:** The VS Code extension (TypeScript) runs locally on the developer's machine and communicates with the backend API (Python/FastAPI) via HTTPS. The backend is fully Dockerizable and can be deployed alongside LiteLLM or run locally for testing.

## Features

- **Rich Sidebar Panel**: Comprehensive spend dashboard with multiple views
- **Status Bar Integration**: Quick glance at current month's LLM spend with color-coded budget state
- **Spend Summary**: Total spend, budget, remaining budget, and usage percentage
- **Model Breakdown**: Spend distribution across different LLM models (GPT-4, Claude, etc.)
- **Project Breakdown**: Spend attribution by project or repository
- **Daily Trend**: Visual chart showing daily spend patterns
- **Budget Warnings**: Visual alerts at 80% and 100% budget thresholds
- **Period Selection**: View spend for today, current week, or current month
- **Manual & Auto Refresh**: Keep data current with configurable refresh intervals
- **Multiple Authentication Methods**: SSO, GitHub token, or internal token support

## Architecture

The extension follows a layered architecture:

```
┌─────────────────────────────────────┐
│   VS Code Extension (TypeScript)    │
├─────────────────────────────────────┤
│  UI Layer                           │
│  - Webview Sidebar (HTML/CSS/JS)    │
│  - Tree View Provider               │
│  - Status Bar Manager               │
├─────────────────────────────────────┤
│  Service Layer                      │
│  - Spend Service                    │
│  - Budget Service                   │
│  - Refresh Service                  │
│  - Project Attribution Service      │
├─────────────────────────────────────┤
│  Data Layer                         │
│  - API Repositories                 │
│  - State Management                 │
│  - Cache Manager                    │
├─────────────────────────────────────┤
│  Infrastructure Layer               │
│  - Authentication Provider          │
│  - API Client (Axios)               │
│  - Configuration Manager            │
│  - Secret Storage                   │
└─────────────────────────────────────┘
              ↓ HTTPS
┌─────────────────────────────────────┐
│   Internal Spend API (Backend)      │
│   - /me/spend/summary               │
│   - /me/spend/by-model              │
│   - /me/spend/by-project            │
│   - /me/spend/daily                 │
│   - /me/budget                      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   LiteLLM Proxy                     │
│   (Spend Tracking & Attribution)    │
└─────────────────────────────────────┘
```

## Project Structure

```
litellm-spend-tracker/
├── src/
│   ├── extension.ts              # Extension entry point
│   ├── constants.ts              # Configuration keys & defaults
│   ├── types/                    # TypeScript interfaces
│   │   ├── spend.ts
│   │   ├── budget.ts
│   │   ├── config.ts
│   │   └── api.ts
│   ├── config/                   # Configuration management
│   ├── auth/                     # Authentication layer
│   │   ├── authProvider.ts
│   │   ├── tokenManager.ts
│   │   ├── identityResolver.ts
│   │   └── strategies/
│   ├── api/                      # API client & repositories
│   │   ├── client.ts
│   │   ├── interceptors.ts
│   │   ├── repositories/
│   │   └── errors.ts
│   ├── cache/                    # Caching layer
│   ├── state/                    # State management
│   ├── services/                 # Business logic services
│   ├── ui/                       # UI components
│   │   ├── sidebar/             # Webview sidebar
│   │   ├── treeView/            # Tree view provider
│   │   ├── statusBar/           # Status bar manager
│   │   └── common/              # Shared UI utilities
│   ├── commands/                 # VS Code commands
│   ├── utils/                    # Utility functions
│   └── test/                     # Test suite
├── resources/
│   ├── icons/                    # Extension icons
│   └── styles/                   # Shared styles
├── docs/                         # Documentation
├── package.json                  # Extension manifest
├── tsconfig.json                 # TypeScript config
└── README.md                     # This file
```

## Installation

### From VSIX (Internal Distribution)

1. Download the `.vsix` file from the shared network location or internal extension gallery
2. In VS Code, go to Extensions view (Ctrl+Shift+X / Cmd+Shift+X)
3. Click the "..." menu and select "Install from VSIX..."
4. Select the downloaded `.vsix` file
5. Reload VS Code when prompted

### From Internal Extension Gallery

If your organization has configured an internal extension gallery:

1. Open Extensions view in VS Code
2. Search for "LLM Spend"
3. Click Install

## Configuration

The extension provides the following configuration options accessible via VS Code Settings:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `llmSpend.apiBaseUrl` | string | `https://spend-api.example.com` | Base URL for the internal spend API |
| `llmSpend.refreshIntervalMinutes` | number | `5` | Automatic refresh interval (1-60 minutes) |
| `llmSpend.defaultPeriod` | string | `month` | Default period: `today`, `week`, or `month` |
| `llmSpend.showTokens` | boolean | `true` | Show token counts in breakdowns |
| `llmSpend.showRequestCount` | boolean | `true` | Show request counts in breakdowns |
| `llmSpend.warningThresholdPercent` | number | `80` | Budget warning threshold (50-100%) |

### Configuring via settings.json

```json
{
  "llmSpend.apiBaseUrl": "http://localhost:8000",
  "llmSpend.refreshIntervalMinutes": 5,
  "llmSpend.defaultPeriod": "month",
  "llmSpend.showTokens": true,
  "llmSpend.showRequestCount": true,
  "llmSpend.warningThresholdPercent": 80
}
```

## Authentication

The extension supports multiple authentication methods:

### 1. SSO (Single Sign-On)

- Uses your organization's SSO provider
- Automatic token refresh
- Recommended for most users

### 2. GitHub Token

- Uses your GitHub authentication token
- Requires backend to accept GitHub tokens
- Useful if you already use GitHub authentication

### 3. Internal Token

- Organization-issued API token
- Stored securely in VS Code SecretStorage
- For environments without SSO

### First-Time Setup

1. Open the LLM Spend sidebar (click the icon in the activity bar)
2. You'll be prompted to authenticate
3. Choose your preferred authentication method
4. Complete the authentication flow
5. Your credentials are stored securely and reused for future sessions

## Usage

### Opening the Sidebar

- **Method 1**: Click the "LLM Spend" icon in the VS Code activity bar
- **Method 2**: Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P) and run "LLM Spend: Open Sidebar"

### Viewing Spend Information

The sidebar displays:

1. **Developer Identity**: Your authenticated user account
2. **Period Selector**: Choose between Today, This Week, or This Month
3. **Summary Section**:
   - Total spend vs budget (e.g., €14.22 / €25.00)
   - Progress bar showing percentage used
   - Remaining budget amount
4. **By Model**: Breakdown of spend by LLM model
   - Model name (e.g., gpt-4.1-mini, claude-haiku)
   - Spend amount and percentage
   - Optional: token count and request count
5. **By Project**: Breakdown of spend by project/repository
   - Project name
   - Spend amount and percentage
   - Optional: request count
6. **Daily Trend**: Chart showing daily spend over the selected period

### Status Bar

The status bar shows your current spend at a glance:

- **Normal**: `LLM: €14.22 / €25` (default color)
- **Warning**: `LLM: 82% used` (yellow, at 80% threshold)
- **Exceeded**: `LLM: budget exceeded` (red, at 100% threshold)
- **Error**: `LLM: unavailable` (red, API unreachable)
- **No Data**: `LLM: €0.00` (default color, no spend recorded)

Click the status bar item to open the sidebar.

### Refreshing Data

- **Manual Refresh**: Click the refresh icon (↻) in the sidebar header
- **Automatic Refresh**: Data refreshes every 5 minutes (configurable)
- **Command**: Run "LLM Spend: Refresh" from Command Palette

### Budget Warnings

The extension provides visual feedback when approaching or exceeding budget:

- **80% Warning**: Yellow warning icon and message in sidebar
- **100% Exceeded**: Red alert with exceeded message
- **Status Bar**: Changes color and text to reflect budget state

## Commands

| Command | Description |
|---------|-------------|
| `LLM Spend: Open Sidebar` | Open the spend sidebar panel |
| `LLM Spend: Refresh` | Manually refresh spend data |
| `LLM Spend: Configure` | Open extension settings |

## Troubleshooting

### "Authentication required" error

**Problem**: Extension prompts for authentication repeatedly

**Solution**:

1. Run "LLM Spend: Configure" from Command Palette
2. Check that `llmSpend.apiBaseUrl` is correct
3. Try signing out and signing in again
4. Contact your administrator if the issue persists

### "Spend service is temporarily unavailable"

**Problem**: API is unreachable

**Solution**:

1. Check your network connection
2. Verify the API base URL in settings
3. Check if the spend API service is running (contact backend team)
4. The extension will show cached data with a "stale" indicator

### No project breakdown shown

**Problem**: "Project-level spend is not available" message

**Solution**:

1. Ensure your workspace has a Git repository initialized
2. Check that the backend is configured to track project metadata
3. Project attribution requires requests to be tagged with workspace/repo information
4. Contact your administrator to enable project tracking

### Spend data seems outdated

**Problem**: Data doesn't reflect recent usage

**Solution**:

1. Click the refresh button in the sidebar
2. Check your `refreshIntervalMinutes` setting
3. Verify network connectivity
4. Check the status bar for error indicators

### Extension not activating

**Problem**: Extension doesn't load or show in sidebar

**Solution**:

1. Check VS Code version (requires 1.85.0 or higher)
2. Open Developer Tools (Help > Toggle Developer Tools) and check for errors
3. Try reinstalling the extension
4. Check the Output panel (View > Output) and select "LLM Spend" channel

## Security

### Data Privacy

- **No Code Access**: The extension never reads, displays, or logs your source code
- **No Prompt Data**: Prompts and completions are never transmitted or stored
- **Minimal Data**: Only spend metadata (amounts, models, timestamps) is displayed
- **Secure Storage**: Credentials stored in VS Code SecretStorage (OS keychain)

### Authorization

- **User-Scoped**: You can only view your own spend data
- **Backend Enforcement**: Server validates JWT and prevents cross-user access
- **No User ID Parameters**: Extension never sends user ID; backend extracts from token

### Network Security

- **HTTPS Only**: All API communication uses HTTPS
- **Token-Based**: Bearer token authentication on all requests
- **Content Security Policy**: Webview uses strict CSP

## Development

### Prerequisites

- Node.js 18+ and npm
- VS Code 1.85.0+
- TypeScript 5.3+

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd litellm-spend-tracker

# Install dependencies
npm install

# Build the extension
npm run build

# Run tests
npm test

# Package for distribution
npm run package
```

### Development Workflow

```bash
# Watch mode for development
npm run watch

# Run in VS Code Extension Development Host
# Press F5 in VS Code to launch debug session

# Lint code
npm run lint

# Format code
npm run format
```

### Testing

```bash
# Run unit tests
npm run test:unit

# Run integration tests
npm run test:integration

# Run all tests with coverage
npm run test:coverage
```

### Building

```bash
# Development build
npm run build

# Production build (minified)
npm run build:prod

# Package as VSIX
npm run package
```

## API Contract

The extension expects the following backend API endpoints:

### GET /me/spend/summary

Returns spend summary for the authenticated user.

**Query Parameters:**

- `period`: `today` | `week` | `month`

**Response:**

```json
{
  "user": "developer@example.com",
  "period": "month",
  "currency": "EUR",
  "spend": 14.22,
  "budget": 25.00,
  "remaining": 10.78,
  "budget_used_percent": 56.88
}
```

### GET /me/spend/by-model

Returns spend breakdown by model.

**Query Parameters:**

- `period`: `today` | `week` | `month`

**Response:**

```json
{
  "period": "month",
  "currency": "EUR",
  "models": [
    {
      "model": "gpt-4.1-mini",
      "spend": 9.10,
      "percent": 64.0,
      "requests": 125,
      "tokens": 345000
    }
  ]
}
```

### GET /me/spend/by-project

Returns spend breakdown by project/repository.

**Query Parameters:**

- `period`: `today` | `week` | `month`

**Response:**

```json
{
  "period": "month",
  "currency": "EUR",
  "projects": [
    {
      "project": "repo-name",
      "spend": 5.40,
      "percent": 38.0,
      "requests": 61
    }
  ]
}
```

### GET /me/spend/daily

Returns daily spend trend.

**Query Parameters:**

- `period`: `today` | `week` | `month`

**Response:**

```json
{
  "period": "month",
  "currency": "EUR",
  "days": [
    {
      "date": "2026-06-25",
      "spend": 1.23,
      "requests": 18,
      "tokens": 42000
    }
  ]
}
```

### GET /me/budget

Returns budget configuration for the user.

**Response:**

```json
{
  "user": "developer@example.com",
  "currency": "EUR",
  "monthly_budget": 25.00,
  "warning_threshold_percent": 80,
  "hard_limit_percent": 100
}
```

## Documentation

- [Architecture Documentation](./docs/architecture.md) - System architecture details
- [API Contracts](./docs/api-contracts.md) - Backend API specification
- [User Guide](./docs/user-guide.md) - End-user documentation

## Roadmap

- **Chat Participant**: `@spend` for natural language queries ("How much did I spend on GPT-4 this week?")
- **Team Manager View**: Aggregate team spend and identify top spenders
- **Cost Allocation**: Tag spend to cost centers or projects
- **Budget Editing**: Request budget increases from VS Code
- **Spend Forecasting**: Predict end-of-month spend based on current trends
- **Anomaly Detection**: Alert on unusual spend patterns
- **Multi-Currency Support**: Display spend in developer's preferred currency
- **Export Functionality**: Export spend data to CSV/Excel

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`npm test && npm run lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Support

For issues or questions:

- **GitHub Issues**: Open an issue on the repository
- **Discussions**: Use GitHub Discussions for questions

## License

MIT License - see [LICENSE](LICENSE) file for details

## Version History

See [CHANGELOG.md](./CHANGELOG.md) for detailed version history.

### Current Version: 1.0.0

**Released:** 2026-06-29

**Major Features:**

- Rich sidebar with spend breakdowns
- Budget warnings and alerts
- Enhanced status bar
- Multiple authentication methods
- Project attribution
- Daily trend visualization

---

**Built with ❤️ by the open-source community**
