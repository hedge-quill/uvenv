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
uvve remove myproject
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

# Create and restore from lockfiles
uvve lock myproject
uvve thaw myproject

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

**When to use `eval` method:**

- ⚙️ Automation scripts and CI/CD
- ⚙️ One-off usage without permanent setup
- ⚙️ Shell functions where integration isn't available

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

| Command                         | Description                                                               |
| ------------------------------- | ------------------------------------------------------------------------- |
| `uvve python install <version>` | Install a Python version using uv                                         |
| `uvve python list`              | List available and installed Python versions                              |
| `uvve create <name> <version>`  | Create a virtual environment with optional metadata                       |
| `uvve activate <name>`          | Activate environment (with shell integration) or print activation snippet |
| `uvve list`                     | List all virtual environments                                             |
| `uvve list --usage`             | List environments with usage statistics                                   |
| `uvve remove <name>`            | Remove a virtual environment                                              |
| `uvve lock <name>`              | Generate a lockfile for the environment                                   |
| `uvve thaw <name>`              | Rebuild environment from lockfile                                         |
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
