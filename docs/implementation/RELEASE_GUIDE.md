# Release Guide

Quick reference for creating and managing CoomerDL releases.

## Creating a New Release

### 1. Prepare the Release

```bash
# Make sure you're on the main branch with latest changes
git checkout main
git pull origin main

# Make sure all tests pass
pytest tests/ -v

# Update version numbers if needed
# - Update version in any version files
# - Update CHANGELOG.md with release notes
```

### 2. Create and Push a Version Tag

```bash
# Create an annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push the tag to GitHub
git push origin v1.0.0
```

**Tag Format**: `v<major>.<minor>.<patch>`
- Examples: `v1.0.0`, `v2.1.3`, `v1.5.0`

### 3. Automated Build Process

Once you push the tag, GitHub Actions will automatically:

1. ✅ Build Windows executable (`.exe`)
2. ✅ Build Linux executable
3. ✅ Build macOS executable
4. ✅ Create a GitHub Release
5. ✅ Upload all executables to the release

### 4. Monitor the Build

1. Go to: https://github.com/primoscope/CoomerDL/actions
2. Click on the "Build and Release" workflow run
3. Watch the build progress for each platform
4. Wait for all jobs to complete (usually 10-15 minutes)

### 5. Verify the Release

1. Go to: https://github.com/primoscope/CoomerDL/releases
2. Your new release should be at the top
3. Check that all three platform files are attached:
   - `CoomerDL-Windows.zip`
   - `CoomerDL-Linux.tar.gz`
   - `CoomerDL-macOS.tar.gz`

### 6. Edit Release Notes (Optional)

The release is created with automatic notes. To customize:

1. Click "Edit" on the release
2. Add detailed changelog:
   ```markdown
   ## What's New
   - New feature X
   - Improved Y
   - Fixed bug Z
   
   ## Bug Fixes
   - Fixed issue #123
   - Fixed crash when...
   
   ## Known Issues
   - Issue X is still present
   ```
3. Save the updated release

## Manual Release (If Needed)

If the automated release fails or you need to release manually:

### Build Locally

```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build the executable
python build.py

# The executable will be in dist/
```

### Create Release Manually

1. Go to: https://github.com/primoscope/CoomerDL/releases/new
2. Choose the tag (or create new tag)
3. Fill in release title: `CoomerDL v1.0.0`
4. Add release notes
5. Upload the executable files
6. Click "Publish release"

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major** (v2.0.0): Breaking changes, major new features
- **Minor** (v1.1.0): New features, backward compatible
- **Patch** (v1.0.1): Bug fixes, small improvements

Examples:
- `v1.0.0` - Initial stable release
- `v1.1.0` - Added new downloader support
- `v1.1.1` - Fixed download bug
- `v2.0.0` - Major UI redesign

## Pre-release Versions

For beta/RC releases:

```bash
# Create a pre-release tag
git tag -a v2.0.0-beta.1 -m "Beta release for v2.0.0"
git push origin v2.0.0-beta.1

# Then mark as pre-release on GitHub
# (Automatic if tag contains beta/alpha/rc)
```

## Hotfix Releases

For urgent fixes:

```bash
# Branch from the release tag
git checkout v1.0.0
git checkout -b hotfix-1.0.1

# Make your fix
git add .
git commit -m "Fix critical bug"

# Merge to main
git checkout main
git merge hotfix-1.0.1

# Tag and release
git tag -a v1.0.1 -m "Hotfix release 1.0.1"
git push origin main
git push origin v1.0.1
```

## Deleting a Release

If you need to remove a release:

```bash
# Delete the tag locally
git tag -d v1.0.0

# Delete the tag on GitHub
git push origin :refs/tags/v1.0.0

# Then delete the release on GitHub web interface
```

## Troubleshooting

### Build fails on GitHub Actions

1. Check the [Actions logs](https://github.com/primoscope/CoomerDL/actions)
2. Look for the specific error message
3. Common issues:
   - Missing dependency: Add to `requirements.txt`
   - PyInstaller error: Update `CoomerDL.spec`
   - Resource not found: Check paths in spec file

### Release not created

1. Check workflow permissions in repository settings
2. Ensure `GITHUB_TOKEN` has write access
3. Verify the workflow ran successfully

### Executables are broken

1. Test locally first: `python build.py`
2. Check hidden imports in `CoomerDL.spec`
3. Verify all resources are included

## CI vs Release Workflows

**CI Workflow** (`.github/workflows/ci.yml`)
- Runs on: Every push and PR
- Purpose: Test and validate code
- Creates artifacts but NOT releases

**Release Workflow** (`.github/workflows/release.yml`)
- Runs on: Version tag push (v*)
- Purpose: Create official release
- Creates GitHub release with downloads

## Quick Commands

```bash
# List all tags
git tag -l

# Show tag details
git show v1.0.0

# Push all tags
git push origin --tags

# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0
```

## Checklist

Before releasing:

- [ ] All tests pass (`pytest tests/`)
- [ ] Code is linted (`flake8 .`)
- [ ] CHANGELOG.md is updated
- [ ] Version numbers are updated
- [ ] Documentation is up to date
- [ ] Local build works (`python build.py`)
- [ ] You're on the main branch
- [ ] All changes are committed and pushed

## Support

For issues with releases:
- Check [Actions logs](https://github.com/primoscope/CoomerDL/actions)
- Review [BUILDING.md](BUILDING.md)
- Open an [issue](https://github.com/primoscope/CoomerDL/issues)
