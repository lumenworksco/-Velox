# Contributing to AlphaFlow

Thank you for considering contributing to AlphaFlow! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, professional, and constructive in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/AlphaFlow.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black ruff mypy

# Install in editable mode
pip install -e .
```

## Code Style

### Python Style Guide

- **Formatting**: Black (line length 100)
- **Linting**: Ruff, Flake8
- **Type Hints**: Required for all public functions
- **Docstrings**: Google style

### Format code before committing

```bash
# Format with black
black app/ core/ --line-length 100

# Lint with ruff
ruff check app/ core/

# Type check with mypy
mypy app/ core/ --strict
```

## Testing

### Writing Tests

- Place tests in `tests/test_core/` or `tests/test_app/`
- Use pytest fixtures for reusable test data
- Aim for 70%+ code coverage
- Test edge cases and error handling

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov=app --cov-report=html

# Run specific test file
pytest tests/test_core/test_indicators.py -v
```

## Pull Request Process

1. **Update Documentation** - Update README.md if needed
2. **Add Tests** - New features require tests
3. **Check Style** - Run black, ruff, mypy
4. **Run Tests** - All tests must pass
5. **Update CHANGELOG** - Document your changes
6. **Submit PR** - Provide clear description

### PR Title Format

```
[Type] Brief description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation update
- style: Code style changes
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance tasks
```

### Example

```
feat: Add support for limit orders in order manager

- Implemented limit order type in OrderManager
- Added validation for limit price
- Updated UI to support limit orders
- Added tests for limit order functionality
```

## Project Structure

```
AlphaFlow/
├── core/           # Trading engine (business logic)
├── app/            # UI layer (PyQt6)
│   ├── widgets/    # Reusable UI components
│   ├── pages/      # Page/tab implementations
│   ├── controllers/# Business logic orchestration
│   └── styles/     # Theming
├── tests/          # Test suite
└── scripts/        # Build and utility scripts
```

## Architecture Guidelines

### Separation of Concerns

- **core/** - Pure Python, no UI dependencies
- **app/** - UI layer, depends on core
- **widgets/** - Reusable UI components
- **pages/** - Full page implementations
- **controllers/** - Coordinate between UI and core

### Best Practices

1. **Keep functions small** - Single responsibility
2. **Use type hints** - Enable static type checking
3. **Document thoroughly** - Docstrings for public APIs
4. **Handle errors gracefully** - User-friendly error messages
5. **Test thoroughly** - Unit and integration tests

## Reporting Bugs

### Before Reporting

1. Check existing issues
2. Test with latest version
3. Gather logs from `logs/` directory

### Bug Report Template

```
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to...
2. Click on...
3. See error...

**Expected behavior**
What you expected to happen.

**Environment:**
- macOS version:
- Python version:
- AlphaFlow version:

**Logs**
Attach relevant logs from `logs/` directory.
```

## Feature Requests

Suggest features via GitHub Issues. Include:

- **Use case** - Why is this needed?
- **Proposed solution** - How should it work?
- **Alternatives** - Other approaches considered

## Questions?

- Open a GitHub Discussion
- Email: support@alphaflow.com

Thank you for contributing to AlphaFlow!
