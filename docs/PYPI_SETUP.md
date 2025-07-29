# PyPI Publishing Setup Guide

This guide explains how to set up automated PyPI publishing for the Redis MCP Server using GitHub Actions and PyPI's trusted publishing feature.

## Overview

The project uses modern Python packaging best practices:

- **Build System**: Hatchling with hatch-vcs for automatic version management from git tags
- **Publishing**: PyPI Trusted Publishing (no API tokens required)
- **Security**: Comprehensive security scanning with bandit and safety
- **Testing**: Multi-platform testing across Python 3.10-3.13
- **Attestations**: Build provenance attestations for supply chain security

## Prerequisites

### 1. PyPI Account Setup

1. Create accounts on both [PyPI](https://pypi.org) and [Test PyPI](https://test.pypi.org)
2. Enable 2FA on both accounts (required for trusted publishing)

### 2. Project Registration

Register your project on both PyPI and Test PyPI:

```bash
# Build the package first
uv build

# Upload to Test PyPI (one-time setup)
uv add --dev twine
uv run twine upload --repository testpypi dist/*

# Upload to PyPI (one-time setup)
uv run twine upload dist/*
```

### 3. Trusted Publishing Configuration

#### For PyPI (Production):

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the details:
   - **PyPI Project Name**: `redis-mcp-server`
   - **Owner**: `redis` (or your GitHub username)
   - **Repository name**: `mcp-redis`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`

#### For Test PyPI:

1. Go to https://test.pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the details:
   - **PyPI Project Name**: `redis-mcp-server`
   - **Owner**: `redis` (or your GitHub username)
   - **Repository name**: `mcp-redis`
   - **Workflow name**: `test-pypi.yml`
   - **Environment name**: `test-pypi`

### 4. GitHub Environment Setup

Create GitHub environments for additional security:

1. Go to your repository settings
2. Navigate to "Environments"
3. Create two environments:
   - `pypi` (for production releases)
   - `test-pypi` (for test releases)
4. Configure protection rules:
   - Require reviewers for production releases
   - Set deployment branch rules

## Release Process

### 1. Version Management

The project uses `hatch-vcs` for automatic version management:

- Versions are automatically derived from git tags
- The `src/version.py` file is automatically updated during build
- Use semantic versioning (e.g., `v1.0.0`, `v1.0.1`, `v2.0.0`)

### 2. Creating a Release

#### Test Release (Pre-release):

1. Create a pre-release tag:
   ```bash
   git tag v1.0.0-rc1
   git push origin v1.0.0-rc1
   ```

2. This triggers the `test-pypi.yml` workflow
3. Package is published to Test PyPI
4. Installation is tested automatically

#### Production Release:

1. Create a GitHub release:
   - Go to your repository's releases page
   - Click "Create a new release"
   - Choose or create a tag (e.g., `v1.0.0`)
   - Add release notes
   - Publish the release

2. This triggers the `release.yml` workflow:
   - Validates version consistency
   - Runs security scans
   - Tests across multiple Python versions
   - Builds the package
   - Publishes to PyPI with attestations
   - Uploads release assets

### 3. Manual Test Release

You can also trigger a test release manually:

1. Go to the "Actions" tab in your repository
2. Select "Test PyPI Release" workflow
3. Click "Run workflow"
4. Enter the version (e.g., `1.0.0-alpha1`)
5. Run the workflow

## Security Features

### 1. Hardened Runners

All workflows use `step-security/harden-runner` to:
- Monitor and audit network traffic
- Detect potential security threats
- Provide security insights

### 2. Dependency Scanning

- **Bandit**: Scans for common security issues in Python code
- **Safety**: Checks for known vulnerabilities in dependencies
- **Dependabot**: Automatically updates dependencies

### 3. Build Attestations

Production releases include build provenance attestations:
- Cryptographically signed build metadata
- Verifiable supply chain information
- Enhanced security for package consumers

## Monitoring and Troubleshooting

### 1. Workflow Status

Monitor workflow runs in the "Actions" tab:
- Green checkmarks indicate successful runs
- Red X marks indicate failures
- Click on runs for detailed logs

### 2. Common Issues

#### Version Mismatch:
- Ensure git tags follow semantic versioning
- Check that `hatch-vcs` can detect the version correctly

#### Trusted Publishing Failures:
- Verify PyPI trusted publishing configuration
- Check GitHub environment settings
- Ensure workflow names match exactly

#### Test Failures:
- Check Redis service availability
- Verify Python version compatibility
- Review test logs for specific errors

### 3. Package Verification

After publishing, verify your package:

```bash
# Install from PyPI
pip install redis-mcp-server==1.0.0

# Test basic functionality
redis-mcp-server --help

# Check package metadata
pip show redis-mcp-server
```

## Best Practices

1. **Always test pre-releases** before production releases
2. **Review security scan results** before publishing
3. **Use semantic versioning** for clear version management
4. **Write comprehensive release notes** for each version
5. **Monitor package downloads** and user feedback
6. **Keep dependencies updated** using Dependabot

## Support

For issues with the publishing process:
- Check the GitHub Actions logs
- Review PyPI trusted publishing documentation
- Open an issue in the repository

For PyPI-specific issues:
- Contact PyPI support
- Check PyPI status page
- Review PyPI documentation
