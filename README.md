# uvve

[![CI](https://github.com/hedge-quill/uvve/workflows/PyPI%20Publish/badge.svg)](https://github.com/hedge-quill/uvve/actions)
[![PyPI version](https://badge.fury.io/py/uvve.svg)](https://badge.fury.io/py/uvve)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A CLI tool for managing Python virtual environments using [uv](https://github.com/astral-sh/uv). Think `pyenv-virtualenv` but powered by the speed of `uv`.

## Features

- 🚀 **Fast**: Leverages uv's speed for Python installation and environment creation
- 🎯 **Simple**: Intuitive CLI commands for common virtual environment operations
- 🔒 **Reproducible**: Lockfile support for consistent environments across systems
- 🐚 **Shell Integration**: Easy activation/deactivation in bash, zsh, fish, and PowerShell
- 📊 **Rich Metadata**: Track environment descriptions, tags, usage patterns, and project links
- 🧹 **Smart Cleanup**: Automatic detection and removal of unused environments
- 📈 **Usage Analytics**: Detailed insights into environment usage and health status
- 🔐 **Azure DevOps Integration**: Seamless setup for private package feeds with automatic authentication

## Installation

```bash
pip install uvve
```

**Prerequisites**: Ensure [uv](https://github.com/astral-sh/uv) is installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quick Start

```bash
# Install shell integration (one-time setup)
uvve shell-integration --print >> ~/.zshrc && source ~/.zshrc

# Install a Python version
uvve python install 3.11

# Create a virtual environment
uvve create myproject 3.11

# Activate the environment
uvve activate myproject

# List environments
uvve list

# Remove an environment
uvve delete myproject
```

## Basic Usage

### Creating Environments

```bash
# Basic environment creation
uvve create myproject 3.11

# Create with rich metadata
uvve create myapi 3.11 --description "Customer API" --add-tag production --add-tag api

# Interactive metadata entry (prompts for description and tags)
uvve create webapp 3.11
```

### Environment Management

```bash
# List all environments
uvve list

# List with usage statistics
uvve list --usage

# Activate an environment (with shell integration)
uvve activate myproject

# Or activate with eval (without shell integration)
eval "$(uvve activate myproject)"

# Set up automatic activation for a directory
uvve local myproject  # Creates .uvve-version file
cd /path/to/project   # Auto-activates when shell integration is installed

# Add packages to active environment
uvve activate myproject
uvve add requests django==4.2  # Uses uv for fast installation

# Remove packages from active environment
uvve remove requests django     # Removes packages and updates tracking

# Create and restore from lockfiles
uvve lock myproject   # Captures all installed packages
uvve thaw myproject   # Restores packages from lockfile

# View installed packages
uvve freeze myproject              # Show all packages
uvve freeze myproject --tracked-only  # Show only manually added packages

# View environment analytics
uvve analytics myproject

# Check utility status of all environments
uvve status

# Find and clean unused environments
uvve cleanup --dry-run
uvve cleanup --unused-for 60 --interactive

# Edit environment metadata
uvve edit myproject --description "My web API" --add-tag "production"

# Clean up unused environments
uvve cleanup --dry-run
```

### Python Version Management

```bash
# Install Python versions
uvve python install 3.11
uvve python install 3.12

# List available and installed versions
uvve python list

# Upgrade existing environments to newer Python versions
uvve python bump 3.12 myproject  # Bump specific environment
uvve activate myproject && uvve python bump 3.12  # Bump active environment
```

## Advanced Usage

### Environment Activation Methods

There are two ways to work with uvve activation:

**Method 1: Shell Integration (Recommended)**

```bash
# One-time setup:
uvve shell-integration >> ~/.zshrc && source ~/.zshrc

# Then simply:
uvve activate myproject
```

**Method 2: Direct Evaluation**

```bash
eval "$(uvve activate myproject)"
```

**Why prefer shell integration?**

- ✅ Simpler command (no `eval` needed)
- ✅ More intuitive for users
- ✅ Consistent with other environment managers
- ✅ One-time setup, lifetime benefit
- ✅ Automatic activation via `.uvve-version` files

**When to use `eval` method:**

- ⚙️ Automation scripts and CI/CD
- ⚙️ One-off usage without permanent setup
- ⚙️ Shell functions where integration isn't available

### Directory-Based Activation

With shell integration installed, you can set up automatic environment activation:

```bash
# Set up a project to auto-activate an environment
cd /path/to/my/project
uvve local myproject  # Creates .uvve-version file

# Now whenever you cd into this directory (or subdirectories)
# the environment will automatically activate
cd /path/to/my/project  # Auto-activates 'myproject'
cd /path/to/my/project/src  # Still uses 'myproject'
cd /path/to/other/project  # Deactivates when leaving

# View which environment is set for current directory
cat .uvve-version  # Shows: myproject
```

**How it works:**

- Shell integration hooks into directory changes
- Looks for `.uvve-version` files in current directory
- Automatically activates the specified environment
- Works across bash, zsh, and fish shells

### Package Management

uvve provides a streamlined workflow for managing packages in your environments:

```bash
# Activate an environment first
uvve activate myproject

# Add packages (uses uv for fast installation)
uvve add requests            # Latest version
uvve add django==4.2        # Specific version
uvve add "fastapi>=0.68.0"   # Version constraint

# Remove packages (uses uv for fast uninstallation)
uvve remove requests         # Remove specific package
uvve remove django fastapi   # Remove multiple packages

# View installed packages
uvve freeze myproject        # All packages
uvve freeze myproject --tracked-only  # Only manually added packages

# Create reproducible environments
uvve lock myproject          # Capture exact versions
uvve thaw myproject          # Restore from lockfile
```

**How it works:**

- `uvve add` requires an active environment (safety feature)
- `uvve remove` requires an active environment and removes packages from tracking
- Uses `uv pip install` and `uv pip uninstall` for fast package management
- Tracks manually added packages in `uvve.requirements.txt`
- Lockfiles capture complete environment state
- `thaw` restores tracked packages automatically

### Python Version Management

uvve provides comprehensive Python version management, including the ability to upgrade existing environments to newer Python versions while preserving dependencies:

```bash
# Install Python versions
uvve python install 3.12     # Install Python 3.12
uvve python install 3.13.5   # Install specific patch version

# List available and installed Python versions
uvve python list

# Bump an existing environment to a newer Python version
# Method 1: From an active environment
uvve activate myproject
uvve python bump 3.12         # Bumps current environment to Python 3.12

# Method 2: Specify environment explicitly
uvve python bump 3.12 myproject  # Bumps 'myproject' to Python 3.12

# Remove unused Python versions
uvve python remove 3.10
```

**Python Version Bumping Process:**

1. **Validation**: Checks that target Python version is available
2. **Dependency Preservation**: Creates lockfile of current packages
3. **Environment Recreation**: Creates temporary environment with new Python version
4. **Package Restoration**: Restores all dependencies from lockfile
5. **Seamless Replacement**: Replaces old environment with new one

**Example: Upgrading a Project**

```bash
# Start with Python 3.11 environment
uvve create myproject 3.11
uvve activate myproject
uvve add requests django

# Later, upgrade to Python 3.12 while keeping all packages
uvve python bump 3.12
# ✓ Environment 'myproject' successfully bumped to Python 3.12
# ✓ All packages (requests, django) preserved

# Verify the upgrade
uvve freeze myproject  # Shows same packages, now on Python 3.12
```

**Use Cases:**

- 🚀 **Project Upgrades**: Modernize projects to latest Python versions
- 🔧 **Testing Compatibility**: Verify code works on different Python versions
- 🛠️ **Maintenance**: Keep development environments current with security updates
- 📦 **Package Requirements**: Upgrade when dependencies require newer Python versions

### Azure DevOps Integration

Set up private package feeds with automatic authentication:

```bash
# Activate an environment first (preferred method with shell integration)
uvve activate myproject

# Or with eval method
# eval "$(uvve activate myproject)"

# Set up Azure DevOps feed
uvve setup-azure --feed-url "https://pkgs.dev.azure.com/myorg/_packaging/myfeed/pypi/simple/" --feed-name "private-feed"

# Add environment variables to your shell
export UV_KEYRING_PROVIDER=subprocess
export UV_INDEX_PRIVATE_FEED_USERNAME=VssSessionToken

# Authenticate with Azure CLI
az login

# Check configuration status
uvve feed-status
```

### Analytics and Cleanup

```bash
# View detailed environment analytics
uvve analytics myproject

# Check health status of all environments
uvve status

# Clean up unused environments
uvve cleanup --unused-for 60 --interactive
uvve cleanup --dry-run  # Preview what would be removed
```

### Shell Completion

```bash
# Auto-install completion for your shell
uvve --install-completion

# Or manually add to your shell config
uvve --show-completion >> ~/.zshrc
```

### Command Reference

| Command                            | Description                                                               |
| ---------------------------------- | ------------------------------------------------------------------------- |
| `uvve python install <version>`    | Install a Python version using uv                                         |
| `uvve python list`                 | List available and installed Python versions                              |
| `uvve python bump <version> [env]` | Upgrade environment to newer Python version while preserving dependencies |
| `uvve python remove <version>`     | Remove an installed Python version                                        |
| `uvve create <name> <version>`  | Create a virtual environment with optional metadata                       |
| `uvve activate <name>`          | Activate environment (with shell integration) or print activation snippet |
| `uvve local <name>`             | Create .uvve-version file for automatic directory-based activation        |
| `uvve add <packages...>`        | Add packages to currently active environment (uses uv)                    |
| `uvve remove <packages...>`     | Remove packages from currently active environment (uses uv)               |
| `uvve list`                     | List all virtual environments                                             |
| `uvve list --usage`             | List environments with usage statistics                                   |
| `uvve delete <name>`            | Delete a virtual environment                                              |
| `uvve lock <name>`              | Generate a lockfile for the environment                                   |
| `uvve thaw <name>`              | Rebuild environment from lockfile                                         |
| `uvve freeze <name>`            | Show installed packages in environment                                    |
| `uvve analytics [name]`         | Show usage analytics and insights                                         |
| `uvve status`                   | Show environment health overview                                          |
| `uvve cleanup`                  | Clean up unused environments                                              |
| `uvve edit <name>`              | Edit environment metadata (description, tags)                             |
| `uvve setup-azure`              | Set up Azure DevOps package feed authentication                           |
| `uvve feed-status`              | Show Azure DevOps configuration status                                    |
| `uvve shell-integration`        | Install shell integration for direct activation                           |
| `uvve --install-completion`     | Install tab completion for your shell                                     |

## Development

uvve is built with Python and welcomes contributions! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

### Quick Setup

```bash
git clone https://github.com/hedge-quill/uvve.git
cd uvve
uv pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
ruff check src/ tests/
black src/ tests/
mypy src/
```

For detailed development guidelines, architecture information, and technical implementation details, see our [Design Document](docs/design.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [uv](https://github.com/astral-sh/uv) - The fast Python package installer and resolver that powers uvve
- [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) - Inspiration for the interface and user experience
