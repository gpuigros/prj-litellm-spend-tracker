# Contributing to LiteLLM Spend Tracker

Thank you for your interest in contributing to LiteLLM Spend Tracker! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- Clear descriptive title
- Detailed description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, VS Code version, etc.)
- Relevant logs or screenshots

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- Clear use case description
- Why this enhancement would be useful
- Possible implementation approach (if you have ideas)

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation as needed
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Development Setup

### Backend (Python/FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

### Extension (TypeScript)

```bash
cd extension
npm install
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Run `ruff check .` and `ruff format .` before committing

### TypeScript

- Follow the existing code style
- Use ESLint and Prettier
- Run `npm run lint` and `npm run format` before committing

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Extension Tests

```bash
cd extension
npm test
```

## Documentation

- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update API documentation for backend changes
- Include JSDoc comments for TypeScript functions

## Questions?

Feel free to open an issue or start a discussion if you have questions!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
