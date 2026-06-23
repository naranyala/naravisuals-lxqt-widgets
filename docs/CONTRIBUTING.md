# Contributing Guide

Guide for contributing to NaraVisuals LXQt Widgets.

## Welcome

Thank you for your interest in contributing to NaraVisuals! This guide will help you get started.

## Ways to Contribute

### Code

- Bug fixes
- New features
- Performance improvements
- Documentation

### Non-Code

- Bug reports
- Feature requests
- Documentation improvements
- Testing
- Translation

## Getting Started

### 1. Fork Repository

```bash
# Fork on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets
```

### 2. Set Up Development Environment

```bash
# Install dependencies
pip install -e .
pip install pytest pytest-cov mypy ruff

# Build C++ plugin
cd native-plugin
mkdir build && cd build
cmake ..
make
cd ../..
```

### 3. Create Branch

```bash
git checkout -b feature/my-feature
```

## Development Workflow

### 1. Make Changes

- Follow coding standards (see `docs/DEVELOPMENT.md`)
- Write tests for new functionality
- Update documentation as needed

### 2. Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=naravisuals

# Check linting
ruff check naravisuals/
ruff format naravisuals/
```

### 3. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

### 4. Push and Create PR

```bash
git push origin feature/my-feature
```

Then create a Pull Request on GitHub.

## Commit Messages

### Format

```
<type>: <subject>

<body>

<footer>
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting |
| `refactor` | Code refactoring |
| `test` | Adding tests |
| `chore` | Maintenance |

### Examples

```
feat: add currency exchange widget

- Add CurrencyProvider for real-time exchange rates
- Support multiple currency pairs
- Add configuration for base/target currencies

Closes #123
```

```
fix: resolve D-Bus connection timeout

- Add connection retry logic
- Increase timeout to 10 seconds
- Add error handling for failed connections

Fixes #456
```

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass
- [ ] Linting passes
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

### PR Description

```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
How to test these changes

## Related Issues
Closes #123
```

### Review Process

1. Automated checks (CI/CD)
2. Code review by maintainer
3. Address feedback
4. Merge when approved

## Bug Reports

### Information to Include

- System information (OS, Python version, Qt version)
- Steps to reproduce
- Expected behavior
- Actual behavior
- Logs (if available)

### Template

```markdown
**Describe the bug**
A clear description of the bug.

**To reproduce**
1. Do this
2. Then that
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.10.12]
- Qt: [e.g., 6.5.0]
- LXQt: [e.g., 1.4.0]

**Logs**
```
journalctl --user -u naravisuals-daemon -n 50
```
```

## Feature Requests

### Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Any other context or screenshots.
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters
- Use docstrings

```python
def get_data(self) -> dict[str, Any]:
    """Return widget data as dictionary.
    
    Returns:
        Dictionary containing widget data.
    """
    pass
```

### C++

- Follow LXQt coding style
- Use Qt naming conventions
- Maximum line length: 100 characters

```cpp
/**
 * Update widget data from D-Bus response.
 * 
 * @param data JSON data from daemon
 */
void updateData(const QJsonObject &data)
{
    // Implementation
}
```

## Testing

### Writing Tests

```python
"""Test module for my feature."""
import pytest
from unittest.mock import patch, MagicMock


class TestMyFeature:
    """Tests for my feature."""
    
    def test_basic(self):
        """Test basic functionality."""
        from naravisuals.my_module import my_function
        
        result = my_function()
        assert result == expected
    
    @patch('naravisuals.my_module.external_call')
    def test_with_mock(self, mock_call):
        """Test with mocked dependency."""
        mock_call.return_value = "mocked"
        
        from naravisuals.my_module import my_function
        result = my_function()
        
        assert result == "mocked"
        mock_call.assert_called_once()
```

### Running Tests

```bash
# All tests
python -m pytest tests/

# Specific file
python -m pytest tests/test_providers.py

# With verbose output
python -m pytest tests/ -v

# Stop on first failure
python -m pytest tests/ -x
```

## Documentation

### Writing Documentation

- Use clear, concise language
- Include code examples
- Keep documentation up to date

### Building Documentation

```bash
# If using Sphinx
cd docs
make html
```

## Translation

### Adding a Translation

1. Create locale file: `naravisuals/locales/<lang>.json`
2. Translate strings
3. Update code to use translations

### String Format

```json
{
    "widget.system_monitor": "System Monitor",
    "widget.weather": "Weather",
    "error.connection": "Connection failed"
}
```

## Release Process

### Version Numbering

Follow Semantic Versioning:
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

### Release Checklist

- [ ] Update version in `setup.py`
- [ ] Update CHANGELOG.md
- [ ] Create release branch
- [ ] Tag release
- [ ] Build packages
- [ ] Publish to PyPI
- [ ] Create GitHub release

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone.

### Our Standards

- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

### Enforcement

Instances of abusive behavior may result in a temporary or permanent ban.

## Getting Help

- GitHub Issues: For bugs and feature requests
- GitHub Discussions: For questions and ideas
- IRC/LXQt channels: For real-time chat

## Recognition

Contributors will be recognized in:
- README.md
- CONTRIBUTORS.md
- Release notes

Thank you for contributing to NaraVisuals!
