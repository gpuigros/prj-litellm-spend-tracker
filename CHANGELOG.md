# Changelog

All notable changes to the LiteLLM Spend Tracker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-29

### Added

- **Backend API (Python/FastAPI)**
  - Complete REST API for spend data aggregation
  - User-scoped authentication via LiteLLM virtual keys
  - Endpoints for spend summary, by-model, by-project, and daily breakdowns
  - Budget tracking with warning and exceeded states
  - Docker containerization with docker-compose setup
  - PostgreSQL integration with LiteLLM database
  - Comprehensive test suite with pytest

- **VS Code Extension**
  - Rich sidebar dashboard with detailed spend visualization
  - Tree view for hierarchical spend breakdown
  - Status bar integration with budget state indicators
  - Multiple time period support (today, week, month)
  - Auto-refresh with configurable intervals
  - In-memory caching for improved performance
  - State management with reactive updates
  - Project attribution service

- **UI Components**
  - Webview-based spend dashboard
  - Interactive period selector
  - Model breakdown display
  - Project breakdown display
  - Daily spend trends
  - Budget status indicators (normal/warning/exceeded)
  - Loading and error states

- **Services Layer**
  - SpendService for data orchestration
  - BudgetService for budget calculations
  - RefreshService for automatic updates
  - ProjectAttributionService for workspace detection

- **State Management**
  - SpendStateManager for spend data
  - BudgetStateManager for budget data
  - Event-driven state updates
  - Reactive UI components

### Technical

- Implemented repository pattern for API access
- Added caching layer with TTL support
- Created comprehensive type definitions
- Structured logging with output channel
- Proper resource disposal on deactivation
- TypeScript 5.3.3
- VS Code engine 1.85.0

[1.0.0]: https://github.com/your-github-username/litellm-spend-tracker/releases/tag/v1.0.0
