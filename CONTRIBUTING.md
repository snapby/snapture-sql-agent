# Contributing to Snapture SQL Agent

Thank you for your interest in contributing to the Snapture SQL Agent! This document provides guidelines and instructions for contributing to this project.

## 📋 Table of Contents

- [Development Setup](#development-setup)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Release Process](#release-process)
- [Contributing Guidelines](#contributing-guidelines)

## 🛠️ Development Setup

### Prerequisites

- **Python 3.12+**
- **UV package manager** (recommended)
- **Git**
- **Docker** (for containerized deployments)

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/snapby/snapture-sql-agent.git
   cd snapture-sql-agent
   ```

2. **Install dependencies**:
   ```bash
   uv sync --all-extras
   ```

3. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Verify installation**:
   ```bash
   make all  # Run all checks
   ```

## 🧪 Code Quality

We maintain high code quality standards using automated tools:

### Available Make Targets

```bash
# Code formatting and linting
make lint          # Fix linting issues
make format        # Format code
make pretty        # Run lint + format

# Type checking
make mypy          # Static type analysis

# Comprehensive checks
make all           # Run all quality checks + cleanup

# Cleanup
make clean-all     # Remove all cache files
```

### Code Style Guidelines

- **Line length**: 79 characters (enforced by Ruff)
- **Import sorting**: Automatic via Ruff
- **Type hints**: Required for public functions
- **Docstrings**: Use Google-style docstrings

## 🔬 Testing

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_example.py
```

### MCP Server Testing

```bash
# Test MCP server functionality
make mcp-inspect         # Interactive inspector
make mcp-inspect-cli     # CLI testing
make mcp-list-tools      # Test tools listing
```

## 🚀 Release Process

We use semantic versioning and automated changelog generation for releases.

### Version Bumping

Use UV's built-in version management with our Make targets:

```bash
# Patch release (0.1.0 → 0.1.1)
make release-patch

# Minor release (0.1.0 → 0.2.0)
make release-minor

# Major release (0.1.0 → 1.0.0)
make release-major
```

### Manual Version Control

If you need more control over versioning:

```bash
# Set specific version
uv version 1.2.3

# Bump with semantic versioning
uv version --bump patch    # 0.1.0 → 0.1.1
uv version --bump minor    # 0.1.0 → 0.2.0  
uv version --bump major    # 0.1.0 → 1.0.0

# Preview changes (dry run)
uv version --bump patch --dry-run
```

### Release Workflow

The release process follows these steps:

1. **Ensure clean working directory**:
   ```bash
   git status  # Should be clean
   ```

2. **Run quality checks**:
   ```bash
   make all  # All checks must pass
   ```

3. **Create release**:
   ```bash
   make release-patch  # or release-minor/release-major
   ```

This will automatically:
- Bump the version in `pyproject.toml`
- Generate changelog from git commits  
- Create and push a Git tag
- Update the lockfile

### Release Make Targets Explained

```bash
# Quick releases with changelog
make release-patch         # Bump patch, generate changelog, tag
make release-minor         # Bump minor, generate changelog, tag  
make release-major         # Bump major, generate changelog, tag

# Manual steps (if needed)
make generate-changelog    # Generate CHANGELOG.md from git history
make tag-current          # Create tag from current version
make push-tags            # Push tags to remote
```

### Changelog Generation

Our changelog is automatically generated from Git commit history:

- **feat**: New features
- **fix**: Bug fixes  
- **docs**: Documentation changes
- **style**: Code style changes
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Test additions/changes
- **chore**: Maintenance tasks

**Example commit messages**:
```bash
git commit -m "feat: add new SQL query optimization"
git commit -m "fix: resolve timeout issues in MCP server"
git commit -m "docs: update API documentation"
```

### Tag Format

Tags follow semantic versioning: `v{MAJOR}.{MINOR}.{PATCH}`

Examples: `v0.1.0`, `v1.0.0`, `v1.2.3`

## 📝 Contributing Guidelines

### Commit Messages

Follow the conventional commits specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Formatting changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

### Pull Request Process

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes with quality checks**:
   ```bash
   # Make your changes
   make all  # Ensure all checks pass
   ```

3. **Commit with conventional messages**:
   ```bash
   git commit -m "feat: add awesome new feature"
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   # Create PR via GitHub interface
   ```

### Code Review Checklist

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] No breaking changes (or properly documented)

## 🐳 Docker Development

### MCP Server Container

Build and test the MCP server container:

```bash
# Build MCP Docker image
./build-mcp-docker.sh

# Run MCP server in HTTP mode
docker run -p 3000:3000 --env-file .env snapture-sql-agent-mcp:latest

# Run MCP server in STDIO mode
docker run -i --env-file .env snapture-sql-agent-mcp:latest \
  fastmcp run mcp_server.py:mcp --transport stdio
```

## 🔧 Troubleshooting

### Common Issues

**UV sync fails**:
```bash
# Clear cache and retry
uv cache clean
uv sync --all-extras
```

**Import errors**:
```bash
# Check Python path
echo $PYTHONPATH
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
```

**MCP server connection issues**:
```bash
# Check server status
make mcp-inspect
```

## 📞 Getting Help

- **Issues**: Create a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check README.md and inline code documentation

---

Thank you for contributing to Snapture SQL Agent! 🚀