# Release Process Documentation

This document outlines the automated release process for the txttoqti project using GitHub Actions and PyPI publishing.

## Overview

The project uses GitHub Actions for automated testing, building, and publishing to PyPI. The process supports both TestPyPI (for testing) and production PyPI publishing.

## Workflows

### 1. Test and Lint (`test-and-lint.yml`)
**Triggers**: Push to main/improving-documentation branches, PRs to main
**Purpose**: Continuous integration testing

- Tests on Python 3.10, 3.11, 3.12
- Runs linting (black, flake8, mypy)
- Tests package building and installation
- Generates test coverage reports

### 2. Test PyPI Publish (`test-pypi-publish.yml`)
**Triggers**: Manual workflow dispatch
**Purpose**: Test publishing to TestPyPI

- Builds package with optional version suffix
- Publishes to TestPyPI
- Tests installation from TestPyPI
- Validates CLI commands work

### 3. Publish to PyPI (`publish-to-pypi.yml`)
**Triggers**: Release published, manual workflow dispatch
**Purpose**: Production publishing

- Builds and validates packages
- Publishes to PyPI on releases
- Can manually publish to TestPyPI or PyPI
- Signs packages with Sigstore
- Uploads signed artifacts to GitHub Release

## Setup Requirements

### 1. PyPI Account Setup

#### Create PyPI Accounts
1. **PyPI**: https://pypi.org/account/register/
2. **TestPyPI**: https://test.pypi.org/account/register/

#### Generate API Tokens
1. **PyPI Token**:
   - Go to https://pypi.org/manage/account/token/
   - Create token with scope "Entire account"
   - Save the token (starts with `pypi-`)

2. **TestPyPI Token**:
   - Go to https://test.pypi.org/manage/account/token/
   - Create token with scope "Entire account" 
   - Save the token (starts with `pypi-`)

### 2. GitHub Repository Setup

#### Configure GitHub Environments

1. **Create TestPyPI Environment**:
   ```
   Repository → Settings → Environments → New environment
   Name: testpypi
   ```

2. **Create PyPI Environment**:
   ```
   Repository → Settings → Environments → New environment
   Name: pypi
   ```

#### Set Up Trusted Publishing (Recommended)

Instead of API tokens, use PyPI's trusted publishing feature:

1. **On PyPI/TestPyPI**:
   - Go to "Publishing" section in your project
   - Add GitHub as trusted publisher
   - Repository: `julihocc/txttoqti`
   - Workflow: `publish-to-pypi.yml`
   - Environment: `pypi` or `testpypi`

2. **Benefits**:
   - No need to store API tokens
   - More secure authentication
   - Automatic token generation

#### Alternative: API Token Secrets (if not using trusted publishing)

If you prefer API tokens over trusted publishing:

1. **Add Secrets**:
   ```
   Repository → Settings → Secrets and variables → Actions
   ```

2. **Required Secrets**:
   - `PYPI_API_TOKEN`: Your PyPI API token
   - `TEST_PYPI_API_TOKEN`: Your TestPyPI API token

## Release Process

### 1. Testing with TestPyPI

#### Manual Test Publish
```bash
# Go to GitHub repository
# Actions → Test PyPI Publish → Run workflow
# Optional: Add version suffix (e.g., "rc1", "dev")
```

#### Automated Test on Push
The test workflow runs automatically on pushes to main branches.

### 2. Production Release

#### Method 1: GitHub Release (Recommended)
1. **Create GitHub Release**:
   ```bash
   gh release create v0.5.0 --title "Release v0.5.0" --notes "Release notes here"
   ```
   
2. **Automatic Publishing**:
   - GitHub Action automatically triggered
   - Builds and publishes to PyPI
   - Signs packages with Sigstore
   - Uploads artifacts to GitHub Release

#### Method 2: Manual Workflow Dispatch
```bash
# Go to GitHub repository
# Actions → Publish to PyPI → Run workflow
# Select target: "pypi"
```

### 3. Version Management

#### Update Version
1. **Update pyproject.toml**:
   ```toml
   version = "0.5.0"
   ```

2. **Update __init__.py**:
   ```python
   __version__ = "0.5.0"
   ```

3. **Commit and Tag**:
   ```bash
   git add pyproject.toml src/txttoqti/__init__.py
   git commit -m "chore: bump version to 0.5.0"
   git tag -a v0.5.0 -m "Release v0.5.0"
   git push origin main --tags
   ```

## Verification

### 1. TestPyPI Installation
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ txttoqti
```

### 2. PyPI Installation
```bash
pip install txttoqti
```

### 3. Verify Installation
```python
import txttoqti
print(txttoqti.__version__)
```

```bash
txttoqti --help
txttoqti-edu --help
```

## Troubleshooting

### Common Issues

1. **Package Already Exists**:
   - PyPI doesn't allow re-uploading same version
   - Use version suffixes for testing: `0.4.0.dev1`

2. **Trusted Publishing Not Working**:
   - Check environment names match exactly
   - Verify workflow file name is correct
   - Ensure repository path is correct

3. **Build Failures**:
   - Check `pyproject.toml` syntax
   - Verify all dependencies are specified
   - Test locally: `python -m build`

4. **Import Errors**:
   - Verify package structure
   - Check `__init__.py` imports
   - Test with: `python -c "import txttoqti"`

### Debug Commands

```bash
# Local build test
python -m build
python -m twine check dist/*

# Local install test
pip install dist/*.whl
python -c "import txttoqti; print(txttoqti.__version__)"

# TestPyPI upload (manual)
python -m twine upload --repository testpypi dist/*
```

## Security Best Practices

1. **Use Trusted Publishing**: Preferred over API tokens
2. **Environment Protection**: Require reviews for production environments
3. **Least Privilege**: Use project-scoped tokens when possible
4. **Token Rotation**: Regularly rotate API tokens if used
5. **Audit Logs**: Monitor PyPI upload logs

## Workflow Customization

### Adding New Checks
Edit `.github/workflows/test-and-lint.yml`:
```yaml
- name: Custom validation
  run: |
    # Your custom checks here
    python scripts/validate_release.py
```

### Modifying Publish Conditions
Edit `.github/workflows/publish-to-pypi.yml`:
```yaml
if: github.event_name == 'release' && !github.event.release.prerelease
```

### Adding Notifications
```yaml
- name: Notify on success
  if: success()
  run: |
    # Send notification (Slack, email, etc.)
```

## Related Documentation

- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Packaging Guide](https://packaging.python.org/)