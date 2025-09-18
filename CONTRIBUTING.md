# Contributing to SpineAPI

Thank you for your interest in contributing to SpineAPI! We welcome contributions from the community and are excited to see what you'll bring to the project.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (for testing containerized features)
- Node.js (for documentation builds)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/spineapi.git
   cd spineapi
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev,llm]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Verify installation**
   ```bash
   pytest
   spineapi --help
   ```

## 📝 Types of Contributions

We welcome many types of contributions:

### 🐛 Bug Reports
- Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include detailed reproduction steps
- Provide system information and logs
- Check if the issue already exists

### ✨ Feature Requests
- Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Describe the problem you're trying to solve
- Explain why this feature would be useful
- Consider implementation details

### 🔧 Code Contributions
- Bug fixes
- New features
- Performance improvements
- Documentation updates
- Test improvements

### 📚 Documentation
- API documentation
- Tutorials and guides
- Example improvements
- Translation efforts

## 🛠️ Development Workflow

### Branch Strategy

We use a simplified Git flow:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature development branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical production fixes

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run tests
   pytest
   
   # Run linting
   pre-commit run --all-files
   
   # Test CLI commands
   spineapi generate examples/petstore.yaml --output ./test-output
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New features
   - `fix:` Bug fixes
   - `docs:` Documentation changes
   - `style:` Code style changes
   - `refactor:` Code refactoring
   - `test:` Test additions or changes
   - `chore:` Maintenance tasks

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

   Then create a pull request on GitHub.

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit
pytest tests/integration
pytest tests/e2e

# Run with coverage
pytest --cov=spineapi --cov-report=html

# Run performance tests
pytest tests/performance
```

### Writing Tests

We use pytest for testing. Test files should be placed in the `tests/` directory:

```python
import pytest
from spineapi.parsers.openapi import OpenAPIParser

def test_parser_validates_spec():
    """Test that the parser correctly validates OpenAPI specs."""
    parser = OpenAPIParser()
    result = parser.parse("tests/fixtures/valid-spec.yaml")
    assert result.is_valid
    assert len(result.endpoints) > 0

@pytest.mark.integration
def test_full_generation_flow():
    """Integration test for complete generation flow."""
    # Test implementation
    pass

@pytest.mark.parametrize("spec_file", [
    "petstore.yaml",
    "ecommerce.yaml",
    "social_media.yaml"
])
def test_example_specs(spec_file):
    """Test all example specifications."""
    # Test implementation
    pass
```

### Test Categories

- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: Tests that verify component interactions
- **E2E Tests**: End-to-end tests that verify complete workflows
- **Performance Tests**: Tests that measure generation speed and memory usage

## 📋 Code Style

### Python Style

We follow PEP 8 with some modifications:

- Line length: 88 characters (Black default)
- Use type hints for all public functions
- Use docstrings for all public classes and functions
- Prefer f-strings for string formatting

Example:

```python
from typing import List, Optional
from pathlib import Path

def generate_api(
    spec_path: Path,
    output_dir: Path,
    features: Optional[List[str]] = None
) -> bool:
    """Generate API code from OpenAPI specification.
    
    Args:
        spec_path: Path to the OpenAPI specification file
        output_dir: Directory to write generated code
        features: Optional list of features to enable
        
    Returns:
        True if generation was successful, False otherwise
        
    Raises:
        ValidationError: If the OpenAPI specification is invalid
        GenerationError: If code generation fails
    """
    # Implementation
    pass
```

### Code Organization

```
spineapi/
├── __init__.py
├── cli.py                  # Command-line interface
├── parsers/                # OpenAPI parsing logic
│   ├── __init__.py
│   ├── openapi.py          # Main parser
│   └── validators.py       # Validation logic
├── generators/             # Code generation
│   ├── __init__.py
│   ├── main.py             # Main generator
│   ├── fastapi.py          # FastAPI-specific generation
│   └── models.py           # Model generation
├── templates/              # Jinja2 templates
│   ├── fastapi/
│   ├── models/
│   └── tests/
├── llm/                    # LLM integration
│   ├── __init__.py
│   ├── enhancer.py         # Code enhancement
│   └── providers.py        # LLM providers
└── utils/                  # Utility functions
    ├── __init__.py
    ├── filesystem.py
    └── logging.py
```

## 🔧 Adding New Features

### Template Development

When adding new templates:

1. Create template files in `spineapi/templates/`
2. Use Jinja2 syntax with our conventions
3. Add template tests in `tests/templates/`
4. Update template documentation

Example template structure:

```jinja2
{# templates/fastapi/router.py.j2 #}
"""{{ endpoint.description }}

Generated by SpineAPI from {{ spec.info.title }} v{{ spec.info.version }}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import {{ model_name }}
from ..schemas import {{ schema_name }}

router = APIRouter(
    prefix="/{{ endpoint.path }}",
    tags=["{{ endpoint.tag }}"]
)

{% for operation in endpoint.operations %}
@router.{{ operation.method }}("{{ operation.path }}")
async def {{ operation.function_name }}(
    {%- for param in operation.parameters %}
    {{ param.name }}: {{ param.type }},
    {%- endfor %}
    db: Session = Depends(get_db)
) -> {{ operation.response_type }}:
    """{{ operation.description }}"""
    # Generated code here
    pass
{% endfor %}
```

### LLM Provider Integration

To add a new LLM provider:

1. Create a provider class in `spineapi/llm/providers/`
2. Implement the `LLMProvider` interface
3. Add provider configuration
4. Add tests for the new provider

```python
from typing import Dict, Any
from .base import LLMProvider

class CustomLLMProvider(LLMProvider):
    """Custom LLM provider implementation."""
    
    def __init__(self, api_key: str, model: str = "default"):
        self.api_key = api_key
        self.model = model
    
    async def enhance_code(
        self, 
        code: str, 
        context: Dict[str, Any]
    ) -> str:
        """Enhance code using the custom LLM service."""
        # Implementation
        pass
    
    async def generate_documentation(
        self, 
        code: str, 
        context: Dict[str, Any]
    ) -> str:
        """Generate documentation for the code."""
        # Implementation
        pass
```

## 📖 Documentation

### Writing Documentation

- Use clear, concise language
- Include code examples
- Test all code examples
- Update table of contents
- Follow the existing structure

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
mkdocs serve

# Build for production
mkdocs build
```

### Documentation Structure

```
docs/
├── index.md                # Main documentation page
├── getting-started.md      # Quick start guide
├── cli-reference.md        # CLI command reference
├── configuration.md        # Configuration options
├── templates.md            # Template development
├── llm-integration.md      # LLM integration guide
├── deployment.md           # Deployment strategies
├── tutorials/              # Step-by-step tutorials
├── examples/               # Usage examples
└── api/                    # API reference
```

## 🏗️ Project Structure

### Directory Overview

```
spineapi/
├── spineapi/               # Main package
├── tests/                  # Test suites
├── examples/               # Example OpenAPI specs
├── docs/                   # Documentation
├── scripts/                # Build and deployment scripts
├── .github/                # GitHub workflows and templates
├── docker/                 # Docker configurations
├── k8s/                    # Kubernetes manifests
└── monitoring/             # Monitoring configurations
```

### Key Files

- `pyproject.toml` - Project configuration and dependencies
- `requirements.txt` - Runtime dependencies
- `setup.py` - Package setup (legacy, prefer pyproject.toml)
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `pytest.ini` - Pytest configuration
- `mypy.ini` - Type checking configuration

## 🚢 Release Process

### Version Management

We use semantic versioning (SemVer):

- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Steps

1. **Update version numbers**
   ```bash
   # Update version in pyproject.toml
   # Update version in spineapi/__init__.py
   # Update CHANGELOG.md
   ```

2. **Create release PR**
   ```bash
   git checkout develop
   git checkout -b release/v1.2.0
   # Make version updates
   git commit -m "chore: bump version to 1.2.0"
   git push origin release/v1.2.0
   ```

3. **Merge to main and tag**
   ```bash
   git checkout main
   git merge release/v1.2.0
   git tag v1.2.0
   git push origin main --tags
   ```

4. **GitHub Actions handles the rest**
   - Runs tests
   - Builds packages
   - Publishes to PyPI
   - Creates GitHub release
   - Updates documentation

## 🆘 Getting Help

### Community Channels

- **GitHub Discussions**: For general questions and discussions
- **GitHub Issues**: For bug reports and feature requests
- **Discord**: For real-time chat and support
- **Stack Overflow**: Tag questions with `spineapi`

### Maintainer Communication

- Tag maintainers in issues: @maintainer-username
- Use draft PRs for early feedback
- Join our weekly contributor calls (details in Discord)

## 📋 Checklist for Contributors

Before submitting a PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventional commits
- [ ] PR description explains the changes
- [ ] No breaking changes without discussion
- [ ] Performance impact is considered
- [ ] Security implications are addressed

## 🎯 Good First Issues

Looking for a place to start? Check out issues labeled:

- `good first issue` - Perfect for new contributors
- `help wanted` - We'd love community help on these
- `documentation` - Documentation improvements needed
- `tests` - Test coverage improvements
- `templates` - New template contributions

## 🙏 Recognition

Contributors are recognized in:

- Release notes
- Contributors section in README
- Annual contributor highlights
- Special recognition for significant contributions

Thank you for contributing to SpineAPI! Together, we're making API development faster and more enjoyable for everyone. 🚀
