# GitHub Actions Workflow Configuration Guide

This document provides a comprehensive guide for configuring and understanding the GitHub Actions workflows in this repository.

## Table of Contents

- [Overview](#overview)
- [Secrets and Permissions](#secrets-and-permissions)
- [Security Analysis](#security-analysis)
- [Repository Settings](#repository-settings)
- [Testing the Workflow](#testing-the-workflow)
- [Troubleshooting](#troubleshooting)

---

## Overview

This repository uses two GitHub Actions workflows:

1. **CI Workflow** (`.github/workflows/ci.yml`) - Runs on every push/PR
   - Lints code with flake8
   - Runs tests on multiple platforms and Python versions
   - Builds executables for verification

2. **Release Workflow** (`.github/workflows/release.yml`) - Runs on version tags
   - Builds executables for Windows, Linux, and macOS
   - Creates GitHub Release
   - Uploads executables as downloadable assets

---

## Secrets and Permissions

### ✅ No Manual Secret Configuration Required

The workflows use **GITHUB_TOKEN**, which is:
- ✅ Automatically provided by GitHub Actions
- ✅ Scoped to the repository only
- ✅ Automatically rotated by GitHub
- ✅ No manual creation or management needed

**Location in Code:**
```yaml
# .github/workflows/release.yml (line 279)
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Permissions Configuration

Both workflows specify explicit permissions following the **principle of least privilege**:

**Release Workflow (needs write access):**
```yaml
permissions:
  contents: write  # Required for creating releases
```

**CI Workflow (read-only):**
```yaml
permissions:
  contents: read  # Minimal permissions for testing
```

---

## Security Analysis

### ✅ Security Best Practices Implemented

#### 1. Token Usage
- Uses GitHub's built-in `GITHUB_TOKEN` (not a personal access token)
- Token is scoped to repository only
- Automatically rotated by GitHub
- No long-lived secrets exposed in code

#### 2. Action Versions - All Patched
All GitHub Actions use secure, up-to-date versions:

| Action | Version | Status |
|--------|---------|--------|
| `actions/checkout` | v4 | ✅ Latest |
| `actions/setup-python` | v5 | ✅ Latest |
| `actions/cache` | v4 | ✅ Latest |
| `actions/upload-artifact` | v4 | ✅ Latest |
| `actions/download-artifact` | v4.1.3 | ✅ **Patched** (CVE-2024-42471) |
| `softprops/action-gh-release` | v1 | ✅ Stable |

**Security Fix Applied:**
- Updated `actions/download-artifact` from v4 to v4.1.3
- Patches CVE-2024-42471 (Arbitrary File Write vulnerability)

#### 3. Workflow Triggers - Controlled Access
**Release Workflow:**
```yaml
on:
  push:
    tags:
      - 'v*'  # Only version tags
  workflow_dispatch:  # Manual trigger only
```

**CI Workflow:**
```yaml
on:
  push:
    branches: [ main, master, develop ]  # Specific branches only
  pull_request:
    branches: [ main, master, develop ]
```

✅ No untrusted trigger sources
✅ No external webhook triggers
✅ No automatic runs from forks (for PRs)

#### 4. Artifact Handling
- Release artifacts: 90-day retention (reasonable for releases)
- CI artifacts: 30-day retention (appropriate for testing)
- No sensitive data stored in artifacts
- Artifacts are scoped to workflow runs

### Security Considerations (Not Vulnerabilities)

#### Unsigned Executables
**Status:** Expected behavior for open-source projects

- Windows/macOS will show security warnings for unsigned executables
- This is **normal** for applications without code signing certificates
- Mitigation: User documentation includes instructions to bypass warnings
- Future enhancement: Consider code signing certificate (~$400/year)

#### Third-Party Actions
**`softprops/action-gh-release@v1`**
- Widely trusted (60,000+ stars on GitHub)
- Actively maintained
- Could optionally pin to specific SHA for extra security
- Current usage (`@v1`) is acceptable and follows GitHub best practices

#### PyInstaller Build Process
- Bundles all dependencies from `requirements.txt`
- No runtime security vulnerabilities introduced
- Dependencies are from trusted sources (PyPI)
- Build process is transparent and reproducible

---

## Repository Settings

### ⚠️ Required Configuration

**Before the workflow can create releases, verify this setting:**

#### 1. Workflow Permissions (REQUIRED)

Navigate to: **Settings → Actions → General → Workflow permissions**

**Required Setting:**
```
☑ Read and write permissions
```

**Why:** Allows workflows to create releases and upload assets

**Current Default:** Many repositories default to "Read repository contents" only

**How to Configure:**
1. Go to your repository on GitHub
2. Click **Settings** (requires admin access)
3. Click **Actions** in the left sidebar
4. Click **General**
5. Scroll to **Workflow permissions**
6. Select **"Read and write permissions"**
7. Click **Save**

**Without this setting:** The release workflow will fail with permission errors when trying to create releases.

### ✅ Recommended (Optional) Configuration

#### 2. Tag Protection

Navigate to: **Settings → Tags → Protected tags**

**Recommended Rule:**
- Pattern: `v*`
- Protection: Require push access to protected branches

**Benefits:**
- Prevents accidental tag creation/deletion
- Ensures only maintainers can trigger releases
- Reduces risk of unauthorized releases

#### 3. Branch Protection

Navigate to: **Settings → Branches**

**Recommended for `main` branch:**
- ☑ Require pull request reviews before merging
- ☑ Require status checks to pass before merging
  - Select: `Lint Code`, `Test on ubuntu-latest - Python 3.11`
- ☑ Require branches to be up to date before merging

**Benefits:**
- Ensures code quality before merging
- Prevents breaking changes in main branch
- Maintains CI/CD pipeline integrity

---

## Testing the Workflow

### First-Time Test (Recommended)

Before creating your first official release, test the workflow:

#### Step 1: Merge the PR
```bash
# Merge this PR to main branch via GitHub UI
```

#### Step 2: Create a Test Tag
```bash
git checkout main
git pull origin main
git tag -a v0.0.1-test -m "Test release workflow"
git push origin v0.0.1-test
```

#### Step 3: Monitor the Workflow
1. Go to **Actions** tab in GitHub
2. Click on the running "Build and Release" workflow
3. Monitor all 4 jobs:
   - ✅ build-windows
   - ✅ build-linux
   - ✅ build-macos
   - ✅ create-release

Expected time: 10-15 minutes

#### Step 4: Verify the Release
1. Go to **Releases** tab
2. Verify "v0.0.1-test" release was created
3. Check that 3 files are attached:
   - `CoomerDL-Windows.zip`
   - `CoomerDL-Linux.tar.gz`
   - `CoomerDL-macOS.tar.gz`
4. Download and test the Windows executable

#### Step 5: Clean Up Test Release
If successful, delete the test release:

1. Delete release from GitHub UI (Releases → Edit → Delete release)
2. Delete tag:
   ```bash
   git push origin :refs/tags/v0.0.1-test
   git tag -d v0.0.1-test
   ```

### Creating Official Releases

Once tested, create releases using semantic versioning:

```bash
# Create version tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag to trigger workflow
git push origin v1.0.0

# Wait 10-15 minutes for builds
# Release will appear automatically at:
# https://github.com/YOUR_USERNAME/CoomerDL/releases
```

**Version Format:**
- `v1.0.0` - Major release (breaking changes)
- `v1.1.0` - Minor release (new features)
- `v1.0.1` - Patch release (bug fixes)

---

## Troubleshooting

### Common Issues

#### Issue: "Resource not accessible by integration" Error

**Cause:** Workflow permissions not configured correctly

**Solution:**
1. Go to Settings → Actions → General
2. Enable "Read and write permissions"
3. Re-run the failed workflow

---

#### Issue: Release Not Created After Successful Builds

**Possible Causes:**
1. Tag doesn't match pattern (must start with `v`)
2. Workflow permissions issue
3. Job condition not met

**Solution:**
```bash
# Ensure tag starts with 'v'
git tag -a v1.0.0 -m "Release"  # ✅ Correct
git tag -a 1.0.0 -m "Release"   # ❌ Won't trigger

# Check workflow logs in Actions tab
# Look for the create-release job
```

---

#### Issue: Build Fails on Specific Platform

**Check:**
1. View the failed job logs in Actions tab
2. Look for missing dependencies or errors
3. Common issues:
   - Missing system dependencies (e.g., `python3-tk` on Linux)
   - PyInstaller incompatibility
   - Resource file not found

**Solution:**
- Fix the issue in code
- Push changes to branch
- Create new tag to trigger rebuild

---

#### Issue: Executable Shows Security Warning

**Status:** This is EXPECTED behavior

**Explanation:**
- Unsigned executables trigger security warnings on Windows and macOS
- This is normal for open-source applications without code signing

**For Windows Users:**
1. Click "More info"
2. Click "Run anyway"

**For macOS Users:**
1. Right-click the app
2. Select "Open"
3. Click "Open" in dialog

**Alternative for macOS:**
```bash
xattr -cr CoomerDL  # Remove quarantine attribute
```

---

#### Issue: Workflow Takes Too Long

**Normal Duration:** 10-15 minutes total

**Job Breakdown:**
- build-windows: ~3-5 minutes
- build-linux: ~3-5 minutes
- build-macos: ~3-5 minutes
- create-release: ~1-2 minutes

**If Longer:**
- Check if jobs are queued (limited concurrent runners)
- PyInstaller may take longer on first build (no cache)
- Subsequent builds will be faster (pip cache)

---

### Manual Workflow Trigger

You can manually trigger the release workflow without pushing a tag:

1. Go to **Actions** tab
2. Select "Build and Release" workflow
3. Click **Run workflow**
4. Select branch
5. Click **Run workflow**

**Note:** Manual runs still require appropriate permissions.

---

## Workflow Architecture

### CI Workflow Flow

```
Push/PR to main
    ↓
┌───────────┐
│   Lint    │  (flake8 checks)
└─────┬─────┘
      ↓
┌───────────┐
│   Test    │  (pytest on 3 OS × 4 Python versions)
└─────┬─────┘
      ↓
┌───────────┐
│   Build   │  (PyInstaller on 3 platforms)
└───────────┘
```

### Release Workflow Flow

```
Push tag v*
    ↓
┌────────────────┬────────────────┬────────────────┐
│ build-windows  │  build-linux   │  build-macos   │
│  (parallel)    │   (parallel)   │   (parallel)   │
└────────┬───────┴────────┬───────┴────────┬───────┘
         │                │                │
         └────────────────┼────────────────┘
                          ↓
                  ┌───────────────┐
                  │ create-release│
                  │ - Download    │
                  │ - Package     │
                  │ - Upload      │
                  └───────────────┘
                          ↓
                  GitHub Release Created
```

---

## Summary Checklist

Before creating your first release, ensure:

- [ ] PR is merged to main branch
- [ ] Repository Settings → Actions → Workflow permissions set to "Read and write"
- [ ] (Optional) Tag protection configured for `v*` pattern
- [ ] (Optional) Branch protection configured for main branch
- [ ] Test release created and verified (v0.0.1-test)
- [ ] Test release and tag cleaned up
- [ ] Ready to create official v1.0.0 release

---

## Support

For issues or questions:
1. Check workflow logs in Actions tab
2. Review this documentation
3. Check [BUILDING.md](BUILDING.md) for build-specific issues
4. Check [RELEASE_GUIDE.md](RELEASE_GUIDE.md) for release process
5. Open an issue on GitHub

---

**Last Updated:** 2026-01-13  
**Workflow Version:** v1.0  
**Status:** Production Ready ✅
