# PyPI Publishing Setup Guide

This guide will help you set up automated PyPI publishing for the txttoqti project.

## Quick Setup Checklist

### ✅ 1. GitHub Repository Settings

#### Create Environments
Go to `Settings → Environments` and create:

1. **testpypi** environment
   - Add protection rules (optional)
   - Required for TestPyPI publishing

2. **pypi** environment  
   - Add protection rules (recommended)
   - Required for production PyPI publishing

#### Protection Rules (Recommended)
For the `pypi` environment:
- ☑️ Required reviewers: Add yourself
- ☑️ Wait timer: 5 minutes (optional)
- ☑️ Deployment branches: Selected branches → `main`

### ✅ 2. PyPI Trusted Publishing Setup

#### TestPyPI Setup
1. Go to https://test.pypi.org/
2. Create account if needed
3. Go to Publishing → Add a new pending publisher
4. Fill in:
   - **PyPI project name**: `txttoqti`
   - **Owner**: `julihocc`  
   - **Repository name**: `txttoqti`
   - **Workflow filename**: `publish-to-pypi.yml`
   - **Environment name**: `testpypi`

#### PyPI Setup  
1. Go to https://pypi.org/
2. Create account if needed
3. Go to Publishing → Add a new pending publisher
4. Fill in:
   - **PyPI project name**: `txttoqti`
   - **Owner**: `julihocc`
   - **Repository name**: `txttoqti` 
   - **Workflow filename**: `publish-to-pypi.yml`
   - **Environment name**: `pypi`

### ✅ 3. Test the Setup

#### Run TestPyPI Workflow
```bash
# Method 1: GitHub Web UI
# Go to Actions → Test PyPI Publish → Run workflow

# Method 2: GitHub CLI
gh workflow run test-pypi-publish.yml
```

#### Check Results
1. Wait for workflow completion
2. Check https://test.pypi.org/project/txttoqti/
3. Verify package uploaded successfully

#### Test Installation
```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ txttoqti

# Verify installation
python -c "import txttoqti; print(txttoqti.__version__)"
txttoqti --help
```

### ✅ 4. Production Release

#### Create Release
```bash
# Create GitHub release (triggers automatic PyPI publish)
gh release create v0.4.1 --title "Release v0.4.1" --notes "Bug fixes and improvements"
```

#### Verify Publication
1. Check workflow completion in Actions
2. Verify at https://pypi.org/project/txttoqti/
3. Test installation: `pip install txttoqti`

## Alternative: API Token Setup

If you prefer API tokens over trusted publishing:

### Generate Tokens
1. **PyPI**: https://pypi.org/manage/account/token/
2. **TestPyPI**: https://test.pypi.org/manage/account/token/

### Add Secrets
Go to `Settings → Secrets and variables → Actions` and add:
- `PYPI_API_TOKEN`: Your PyPI token
- `TEST_PYPI_API_TOKEN`: Your TestPyPI token

### Update Workflows
Modify workflows to use token-based authentication instead of trusted publishing.

## Troubleshooting

### Common Issues

#### "No such environment" Error
- Verify environment names in repository settings
- Ensure environment names match workflow files exactly

#### "Trusted publisher not found" Error
- Check PyPI trusted publisher configuration
- Verify repository owner, name, workflow, and environment names

#### "Package already exists" Error
- PyPI doesn't allow re-uploading same version
- Increment version number in `pyproject.toml` and `__init__.py`

#### Workflow Permission Errors
- Check repository Actions permissions
- Ensure `id-token: write` permissions are set

### Debug Steps

1. **Check workflow logs** in GitHub Actions
2. **Verify environment setup** in repository settings
3. **Test local build**:
   ```bash
   python -m build
   python -m twine check dist/*
   ```

4. **Test package import**:
   ```bash
   pip install dist/*.whl
   python -c "import txttoqti"
   ```

## Security Considerations

### Trusted Publishing Benefits
- ✅ No long-lived tokens to manage
- ✅ Automatic token generation per workflow run
- ✅ Scoped to specific repository and workflow
- ✅ Audit trail through GitHub Actions

### Environment Protection
- ✅ Require manual approval for production deployments
- ✅ Restrict to specific branches (main)
- ✅ Add wait timers for final review

### Monitoring
- ✅ Monitor workflow runs in GitHub Actions
- ✅ Check PyPI project security logs
- ✅ Set up notifications for failed deployments

## Next Steps

1. ✅ Complete the setup checklist above
2. ✅ Test with TestPyPI first
3. ✅ Create your first automated release
4. ✅ Monitor and iterate on the process

For detailed information, see [docs/release-process.md](../docs/release-process.md).