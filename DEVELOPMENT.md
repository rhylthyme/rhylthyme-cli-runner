# Development Setup

## Quick Start

```bash
# Install the package with development dependencies
pip install -e ".[dev]"

# Or use the Makefile shortcut
make install-dev
```

## Development Dependencies

All development dependencies are managed in `setup.py` under the `extras_require` section:

- **Testing**: pytest, pytest-cov, pytest-mock, pytest-xdist
- **Code Quality**: black, flake8, isort, mypy  
- **Testing Utilities**: responses, freezegun

## Available Extras

```bash
# Install with development tools
pip install -e ".[dev]"

# Install with documentation tools  
pip install -e ".[docs]"

# Install with build tools
pip install -e ".[build]"

# Install everything
pip install -e ".[dev,docs,build]"
```

## Why setup.py instead of requirements-dev.txt?

✅ **Advantages of using setup.py:**
- **Single source of truth** for all dependencies
- **Semantic grouping** with extras_require (dev, docs, build)
- **Version constraints** managed alongside main dependencies
- **Standard Python packaging** approach
- **Easier maintenance** - one file to update

❌ **Disadvantages of requirements-dev.txt:**
- Duplicate dependency management
- Can get out of sync with setup.py
- No semantic grouping
- Extra file to maintain

## Development Workflow

```bash
# Setup development environment
make dev-setup

# Run tests
make test-fast          # Quick tests
make test              # All tests  
make coverage          # With coverage

# Code quality
make format            # Format code
make lint             # Check linting
make type-check       # Type checking

# Full CI simulation
make ci-test
```