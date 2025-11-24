# GitHub Actions Workflows Documentation

This document describes all the GitHub Actions workflows configured for this repository.

## Overview

The repository uses 12 workflows to ensure code quality, security, and proper deployment. Each workflow is designed for a specific purpose and runs on different triggers.

## Active Workflows

### 1. Comprehensive CI (`ci.yml`)
**Purpose**: Main continuous integration workflow with comprehensive testing and security scanning.

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs**:
- **lint-and-test**: 
  - Runs flake8 for code quality
  - Checks code formatting with black
  - Performs type checking with mypy
  - Initializes database
  - Tests Flask application startup
  - Runs pytest test suite
  
- **security-scan**:
  - Scans dependencies for vulnerabilities (safety)
  - Performs static code analysis (bandit)
  - Uploads security reports as artifacts

- **build-status**: 
  - Aggregates results from all jobs
  - Fails if critical jobs fail

**Permissions**: `contents: read`, `pull-requests: write`

---

### 2. Python Application (`python-app.yml`)
**Purpose**: Standard Python CI workflow for single Python version testing.

**Triggers**:
- Push to `main` branch
- Pull requests to `main` branch

**Jobs**:
- Installs dependencies
- Runs flake8 linting
- Initializes database
- Runs pytest tests

**Python Version**: 3.10

**Permissions**: `contents: read`

---

### 3. Python Package (`python-package.yml`)
**Purpose**: Multi-version Python testing to ensure compatibility.

**Triggers**:
- Push to `main` branch
- Pull requests to `main` branch

**Jobs**:
- Tests against Python 3.9, 3.10, and 3.11
- Runs flake8 linting
- Initializes database
- Runs pytest tests

**Permissions**: `contents: read`

---

### 4. Python Publish (`python-publish.yml`)
**Purpose**: Publishes the package to PyPI when a release is created.

**Triggers**:
- Release published

**Jobs**:
- Builds the package
- Publishes to PyPI using API token

**Requirements**: 
- `PYPI_API_TOKEN` secret must be configured

**Permissions**: `contents: read`, `id-token: write`

---

### 5. CodeQL Analysis (`codeql.yml`)
**Purpose**: Advanced security scanning and vulnerability detection.

**Triggers**:
- Push to `main` branch
- Pull requests to `main` branch
- Scheduled: Every Monday at 5:33 UTC

**Languages Analyzed**:
- Python
- JavaScript

**Permissions**: `actions: write`, `security-events: write`

---

### 6. Dependency Review (`dependency-review.yml`)
**Purpose**: Reviews dependency changes in pull requests for known vulnerabilities.

**Triggers**:
- Pull requests to `main` branch

**Features**:
- Comments summary in PR
- Fails on moderate severity or higher
- Denies GPL-1.0-or-later and LGPL-2.0-or-later licenses

**Permissions**: `contents: read`, `pull-requests: write`

---

### 7. Frogbot Scan (`frogbot-scan-pr.yml`)
**Purpose**: JFrog Xray security scanning for pull requests.

**Triggers**:
- Pull requests opened or synchronized

**Requirements**:
- `JF_URL` secret
- `JF_ACCESS_TOKEN` secret
- Approval from `frogbot` environment

**Permissions**: Multiple (comprehensive security scanning)

---

### 8. Mobb/CodeQL (`mobb-codeql.yaml`)
**Purpose**: Automated security vulnerability fixing using Mobb.

**Triggers**:
- Pull requests to any branch

**Features**:
- Runs CodeQL analysis
- Generates automated fixes using Mobb
- Posts fixes as PR comments

**Requirements**:
- `MOBB_API_TOKEN` secret

**Permissions**: `pull-requests: write`, `contents: read`, `actions: read`

---

### 9. Node.js with Gulp (`npm-gulp.yml`)
**Purpose**: Builds and tests JavaScript/frontend assets.

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual workflow dispatch

**Jobs**:
- **lint-and-security**: ESLint, security checks
- **build-and-test**: Builds for Node 18.x, 20.x, 22.x
- **deploy**: Deploys to production (main branch only)
- **notify**: Sends build notifications

**Permissions**: `contents: read`, `security-events: write`, `checks: write`

---

### 10. Static Pages (`static.yml`)
**Purpose**: Deploys static content to GitHub Pages.

**Triggers**:
- Push to `main` branch
- Manual workflow dispatch

**Features**:
- Uploads entire repository as static content
- Deploys to GitHub Pages

**Permissions**: `contents: read`, `pages: write`, `id-token: write`

---

### 11. Issue Summarizer (`summary.yml`)
**Purpose**: Uses AI to automatically summarize new issues.

**Triggers**:
- New issues opened

**Features**:
- Uses GitHub Actions AI inference
- Posts summary as issue comment

**Permissions**: Multiple (issue management)

---

### 12. Pull Request Labeler (`label.yml`)
**Purpose**: Automatically labels pull requests based on changed files.

**Triggers**:
- Pull request created or updated

**Configuration**: Uses `.github/labeler.yml` for label rules

**Permissions**: `contents: write`, `pull-requests: write`

---

## Removed Workflows

The following workflows were removed as they are not applicable to this project:

1. **rubocop.yml** - No Ruby code in repository
2. **jekyll-gh-pages.yml** - Conflicted with static.yml
3. **clj-watson.yml** - No Clojure code, had syntax errors
4. **python-package-conda.yml** - No environment.yml, syntax errors
5. **issues-summary.yml** - Invalid syntax, not standard action

---

## Security Best Practices

All workflows follow these security principles:

1. **Principle of Least Privilege**: Each workflow has only the minimum required permissions
2. **Dependency Scanning**: Multiple tools scan for vulnerabilities (Safety, Bandit, CodeQL, Frogbot)
3. **Secrets Management**: All sensitive data stored as GitHub secrets
4. **SARIF Reports**: Security findings uploaded in standard format
5. **Automated Fixes**: Mobb provides automated security fix suggestions

---

## Configuration Files

- `.github/labeler.yml` - Label rules for PR labeler
- `gulpfile.js` - Gulp build configuration
- `package.json` - Node.js dependencies and scripts
- `requirements.txt` - Python dependencies

---

## Troubleshooting

### Workflow Fails with Permission Errors
- Check that required secrets are configured in repository settings
- Verify workflow permissions in the YAML file

### Python Tests Fail
- Ensure all dependencies in requirements.txt are up to date
- Check that database initialization completes successfully
- Review test logs in the workflow run

### Node.js Build Fails
- Verify package.json and package-lock.json are in sync
- Check that gulpfile.js is present and valid
- Ensure Node.js version compatibility (18.x, 20.x, 22.x)

### Security Scan Failures
- Review SARIF reports uploaded as artifacts
- Check security scan logs for specific vulnerabilities
- Apply suggested fixes from Mobb or manually update dependencies

---

## Maintenance

### Adding a New Workflow
1. Create a new YAML file in `.github/workflows/`
2. Follow the naming convention: lowercase with hyphens
3. Use minimal permissions (principle of least privilege)
4. Add documentation to this file
5. Test the workflow on a branch before merging to main

### Updating Workflow Permissions
1. Review what the workflow actually needs to do
2. Grant only the minimum required permissions
3. Avoid `write-all` or overly broad permissions
4. Document why each permission is needed

### Deprecating a Workflow
1. Remove the workflow file from `.github/workflows/`
2. Update this documentation
3. Notify team members of the change
4. Monitor for any dependent processes

---

## Contact

For questions about workflows, please:
- Open an issue in the repository
- Contact the DevOps team
- Review GitHub Actions documentation: https://docs.github.com/en/actions

---

**Last Updated**: 2025-10-14
**Maintained By**: DevOps Team
