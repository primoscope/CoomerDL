# Building CoomerDL

This document describes how to build CoomerDL executables for distribution.

## Table of Contents

- [Quick Start](#quick-start)
- [Building Locally](#building-locally)
- [Building via GitHub Actions](#building-via-github-actions)
- [Creating a Release](#creating-a-release)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Build locally (all platforms)

```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build using the build script (recommended)
python build.py

# Or build directly with PyInstaller
pyinstaller CoomerDL.spec
```

The executable will be created in the `dist/` directory.

## Building Locally

### Prerequisites

1. **Python 3.8 or later** installed
2. **Git** (for version control)
3. **All dependencies** from `requirements.txt`
4. **PyInstaller** (`pip install pyinstaller`)

### Windows

```powershell
# Clone the repository
git clone https://github.com/primoscope/CoomerDL.git
cd CoomerDL

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build the executable
python build.py

# Or use PyInstaller directly
pyinstaller CoomerDL.spec

# The executable will be at: dist\CoomerDL.exe
```

### Linux

```bash
# Clone the repository
git clone https://github.com/primoscope/CoomerDL.git
cd CoomerDL

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3-tk

# Install Python dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build the executable
python build.py

# The executable will be at: dist/CoomerDL
# Make it executable
chmod +x dist/CoomerDL
```

### macOS

```bash
# Clone the repository
git clone https://github.com/primoscope/CoomerDL.git
cd CoomerDL

# Install Python dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build the executable
python build.py

# The executable will be at: dist/CoomerDL
# Make it executable
chmod +x dist/CoomerDL
```

## Building via GitHub Actions

CoomerDL includes automated build workflows that run on GitHub Actions.

### Continuous Integration (CI)

The CI workflow (`.github/workflows/ci.yml`) runs on every push and pull request:

- **Lints** the code with flake8
- **Tests** on multiple platforms (Windows, Linux, macOS) and Python versions (3.9-3.12)
- **Builds** executables for all platforms
- **Uploads artifacts** that can be downloaded from the Actions tab

To access build artifacts:
1. Go to the [Actions tab](https://github.com/primoscope/CoomerDL/actions)
2. Click on the latest workflow run
3. Scroll down to "Artifacts" section
4. Download the builds for your platform

### Release Workflow

The release workflow (`.github/workflows/release.yml`) creates official releases automatically.

## Creating a Release

To create a new release with executables:

### 1. Tag a Version

```bash
# Create and push a version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

Tag format: `v<major>.<minor>.<patch>` (e.g., `v1.0.0`, `v2.1.3`)

### 2. Automatic Build and Release

When you push a version tag, GitHub Actions will automatically:

1. ✅ Build executables for Windows, Linux, and macOS
2. ✅ Create a GitHub Release with the version tag
3. ✅ Upload all executables to the release
4. ✅ Generate release notes with download instructions

### 3. Monitor the Build

1. Go to [GitHub Actions](https://github.com/primoscope/CoomerDL/actions)
2. Click on the "Build and Release" workflow run
3. Monitor the build progress for each platform
4. Once complete, the release will appear in [Releases](https://github.com/primoscope/CoomerDL/releases)

### 4. Edit Release Notes (Optional)

After the automatic release is created, you can:

1. Go to [Releases](https://github.com/primoscope/CoomerDL/releases)
2. Click "Edit" on the new release
3. Add more details about changes, features, and bug fixes
4. Save the updated release

## Technical Details

### PyInstaller Spec File

CoomerDL uses a custom PyInstaller spec file (`CoomerDL.spec`) that:

- **Includes all resources**: Images, icons, config files
- **Bundles dependencies**: customtkinter, yt-dlp, gallery-dl, etc.
- **Collects hidden imports**: Ensures all modules are included
- **Sets app icon**: Uses the CoomerDL icon for the executable
- **Configures windowed mode**: No console window on startup (Windows)
- **Optimizes size**: Excludes unnecessary packages (matplotlib, numpy, etc.)

### Build Output

After building, you'll have:

```
dist/
├── CoomerDL.exe       (Windows)
└── CoomerDL           (Linux/macOS)
```

The executable is **standalone** and includes:
- Python interpreter
- All Python dependencies
- Application code
- Resources (images, icons, configs)

### Size Optimization

The spec file excludes these packages to reduce size:
- `matplotlib`
- `numpy`
- `pandas`
- `scipy`
- `pytest`
- `setuptools`

If you need any of these, remove them from the `excludes` list in `CoomerDL.spec`.

## Troubleshooting

### Build Errors

#### "PyInstaller not found"

```bash
pip install pyinstaller
```

#### "ModuleNotFoundError" during build

Add the missing module to `hiddenimports` in `CoomerDL.spec`:

```python
hiddenimports += [
    'your.missing.module',
]
```

#### "Failed to execute script"

This usually means a dependency is missing. Check:
1. All imports in your code
2. `hiddenimports` in `CoomerDL.spec`
3. Data files in `datas` list

### Runtime Errors

#### "Cannot find resources"

Ensure resources are properly included in the spec file:

```python
datas += [
    ('resources', 'resources'),
]
```

#### "Missing DLL" (Windows)

Some packages need system DLLs. Solutions:
1. Install Visual C++ Redistributable
2. Copy missing DLLs to the `dist/` folder
3. Use `--hidden-import` flag with PyInstaller

#### Executable is too large

To reduce size:
1. Remove unused dependencies from `requirements.txt`
2. Add more packages to `excludes` in the spec file
3. Use UPX compression (already enabled in spec)

### Platform-Specific Issues

#### Windows: "Windows Defender SmartScreen"

Unsigned executables trigger warnings. Users need to:
1. Click "More info"
2. Click "Run anyway"

To avoid this, sign the executable (requires code signing certificate).

#### macOS: "App can't be opened because it is from an unidentified developer"

Users need to:
1. Right-click the app
2. Select "Open"
3. Click "Open" in the dialog

Or use: `xattr -cr CoomerDL` to remove quarantine attribute.

#### Linux: "Permission denied"

Make the executable:
```bash
chmod +x dist/CoomerDL
```

## Build Script Options

The `build.py` script supports several options:

```bash
# Clean build (remove all artifacts first)
python build.py --clean

# Debug build (with console window)
python build.py --debug

# Both
python build.py --clean --debug
```

## CI/CD Configuration

### CI Workflow (`ci.yml`)

Runs on: `push`, `pull_request` to `main`/`master`/`develop`

Jobs:
1. **Lint**: Code quality checks with flake8
2. **Test**: Run test suite on multiple platforms/versions
3. **Build**: Create executables for Windows, Linux, macOS

### Release Workflow (`release.yml`)

Runs on: `push` of version tags (`v*`)

Jobs:
1. **Build Windows**: Create Windows `.exe`
2. **Build Linux**: Create Linux binary
3. **Build macOS**: Create macOS binary
4. **Create Release**: Package and upload to GitHub Releases

## Best Practices

1. **Test before tagging**: Always test locally before creating a release tag
2. **Semantic versioning**: Use `v<major>.<minor>.<patch>` format
3. **Changelog**: Update CHANGELOG.md before releasing
4. **Test executables**: Download and test artifacts before publishing
5. **Release notes**: Add detailed notes about changes, fixes, and new features

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)

---

**Questions?** Open an issue at [GitHub Issues](https://github.com/primoscope/CoomerDL/issues)
