# uvve

[![CI](https://github.com/mgale694/uvve/workflows/CI/badge.svg)](https://github.com/mgale694/uvve/actions)
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

## Quick Start

### Installation

```bash
pip install uvve
```

### Prerequisites

Ensure [uv](https://github.com/astral-sh/uv) is installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Basic Usage

```bash
# Install shell integration (one-time setup)
uvve shell-integration >> ~/.zshrc && source ~/.zshrc

# Install a Python version
uvve python install 3.11

# List available Python versions
uvve python list

# Create a virtual environment
uvve create myproject 3.11

# Create with rich metadata
uvve create myapi 3.11 --description "Customer API" --add-tag production --add-tag api

# Interactive metadata entry (prompts for description and tags)
uvve create webapp 3.11

# Activate the environment (with shell integration)
uvve activate myproject

# Set up Azure DevOps package feed (optional)
uvve setup-azure --feed-url "https://pkgs.dev.azure.com/myorg/_packaging/myfeed/pypi/simple/"

# List environments
uvve list

# Create a lockfile
uvve lock myproject

# View environment analytics
uvve analytics myproject

# Check environment health
uvve status

# Clean up unused environments
uvve cleanup --dry-run

# Edit environment metadata
uvve edit myproject --description "My web API" --add-tag "production"

# Remove an environment
uvve remove myproject
```

## Understanding Environment Activation

There are two ways to work with uvve activation:

### Method 1: Direct Evaluation (Recommended)

```bash
eval "$(uvve activate myproject)"
```

This **actually activates** the environment in your current shell session. The `eval` command executes the activation script that `uvve activate` outputs.

### Method 2: Manual Activation

```bash
uvve activate myproject
# Outputs: source /Users/username/.uvve/myproject/bin/activate

# Then manually run the output:
source /Users/username/.uvve/myproject/bin/activate
```

This **just shows** the activation command. You need to copy and run the output manually.

**Why use `eval`?**

- ✅ Activates the environment immediately
- ✅ Works in scripts and automation
- ✅ Single command instead of two steps
- ✅ No copy-pasting required

## Commands

| Command                         | Description                                         |
| ------------------------------- | --------------------------------------------------- |
| `uvve python install <version>` | Install a Python version using uv                   |
| `uvve python list`              | List available and installed Python versions        |
| `uvve create <name> <version>`  | Create a virtual environment with optional metadata |
| `uvve activate <name>`          | Print shell activation snippet                      |
| `uvve list`                     | List all virtual environments                       |
| `uvve list --usage`             | List environments with usage statistics             |
| `uvve remove <name>`            | Remove a virtual environment                        |
| `uvve lock <name>`              | Generate a lockfile for the environment             |
| `uvve thaw <name>`              | Rebuild environment from lockfile                   |
| `uvve analytics [name]`         | Show usage analytics and insights                   |
| `uvve status`                   | Show environment health overview                    |
| `uvve cleanup`                  | Clean up unused environments                        |
| `uvve edit <name>`              | Edit environment metadata (description, tags)       |
| `uvve setup-azure`              | Set up Azure DevOps package feed authentication     |
| `uvve azure-status`             | Show Azure DevOps configuration status              |
| `uvve shell-integration`        | Install shell integration for direct activation     |
| `uvve --install-completion`     | Install tab completion for your shell               |
| `uvve --show-completion`        | Show completion script for manual installation      |

## Environment Storage

Virtual environments are stored in `~/.uvve/`:

```
~/.uvve/
├── myproject/
│   ├── bin/activate           # Activation script
│   ├── lib/python3.11/        # Python packages
│   ├── uvve.lock            # Lockfile (TOML format)
│   └── uvve.meta.json       # Metadata (usage, tags, description)
└── another-env/
    └── ...
```

## Rich Metadata and Analytics

uvve tracks rich metadata for each environment including:

- **Usage Statistics**: Activation count, last used date, usage frequency
- **Descriptions and Tags**: Organize environments with custom descriptions and tags
- **Project Linking**: Associate environments with project directories
- **Size Tracking**: Monitor disk usage for cleanup decisions

### Analytics Commands

```bash
# View detailed analytics for an environment
uvve analytics myproject

# Check health status of all environments
uvve status

# Find and clean unused environments
uvve cleanup --dry-run
uvve cleanup --unused-for 60 --interactive

# Edit environment metadata
uvve edit myproject --description "Production API server"
uvve edit myproject --add-tag "production" --add-tag "api"

# List with usage information
uvve list --usage --sort-by usage
```

## Shell Integration

### Option 1: Built-in Shell Integration (Recommended)

Install uvve's shell integration to make `uvve activate` work directly:

````bash
# One-time setup:
uvve shell-integration >> ~/.zshrc  # for zsh
uvve shell-integration >> ~/.bashrc # for bash

**After installation, you can use:**

```bash
uvve activate myproject    # No eval needed!
uvve list                  # Works normally
uvve python install 3.12  # Works normally
````

### Option 2: Manual Shell Functions

Add to your shell config for easier activation:

> **Note:** These functions use `eval "$(uvve activate ...)"` to actually activate the environment, not just print the activation command.

### Bash/Zsh

```bash
# Add to ~/.bashrc or ~/.zshrc
uvactivate() {
    if [ -z "$1" ]; then
        echo "Usage: uvactivate <environment_name>"
        return 1
    fi
    eval "$(uvve activate "$1")"
}
```

### Fish

```fish
# Add to ~/.config/fish/config.fish
function uvactivate
    if test (count $argv) -eq 0
        echo "Usage: uvactivate <environment_name>"
        return 1
    end
    eval (uvve activate $argv[1])
end
```

## Shell Completion

uvve supports tab completion for commands and arguments:

### Auto-Install Completion

```bash
# Install completion for your current shell
uvve --install-completion

# Restart your terminal or source your shell config
```

### Manual Installation

If auto-install doesn't work, you can manually add completion:

```bash
# Show the completion script for your shell
uvve --show-completion

# Add it to your shell config manually
# Add it to your shell config manually
```

## Azure DevOps Integration

uvve provides seamless integration with Azure DevOps package feeds, allowing you to install private packages alongside public PyPI packages. This integration automatically handles authentication setup and keyring configuration.

### Quick Setup

```bash
# 1. Activate a uvve environment
eval "$(uvve activate myproject)"

# 2. Set up Azure DevOps feed (auto-detects active environment)
uvve setup-azure --feed-url "https://pkgs.dev.azure.com/myorg/_packaging/myfeed/pypi/simple/" --feed-name "private-feed"

# 3. Add environment variables to your shell
export UV_KEYRING_PROVIDER=subprocess
export UV_INDEX_PRIVATE_FEED_USERNAME=VssSessionToken

# 4. Authenticate with Azure CLI
az login
```

### Features

- 🔧 **Auto-Detection**: Automatically detects active uvve environments
- 📦 **Keyring Installation**: Installs `keyring` and `artifacts-keyring` into the environment
- 🌐 **PyPI Preservation**: Ensures PyPI access is maintained alongside private feeds
- 🔗 **Multiple Feeds**: Support for multiple Azure DevOps feeds in the same environment
- 📊 **Status Monitoring**: Check configuration status with `uvve azure-status`

### Commands

| Command             | Description                                     |
| ------------------- | ----------------------------------------------- |
| `uvve setup-azure`  | Set up Azure DevOps package feed authentication |
| `uvve azure-status` | Show Azure DevOps configuration status          |

### Detailed Setup Process

#### 1. Create and Activate Environment

```bash
# Create a new environment
uvve create myproject 3.11 --description "Project with private packages"

# Activate it
eval "$(uvve activate myproject)"
```

#### 2. Configure Azure Feed

With an active environment, uvve will automatically install keyring packages into it:

```bash
uvve setup-azure
  --feed-url "https://pkgs.dev.azure.com/myorg/_packaging/myfeed/pypi/simple/"
  --feed-name "private-feed"
```

Without an active environment, you'll be prompted to choose one:

```bash
uvve setup-azure
  --feed-url "https://pkgs.dev.azure.com/myorg/_packaging/myfeed/pypi/simple/"
  --feed-name "private-feed"
```

#### 3. Environment Variables

Add the generated environment variables to your shell configuration:

```bash
# For bash/zsh (~/.bashrc or ~/.zshrc)
export UV_KEYRING_PROVIDER=subprocess
export UV_INDEX_PRIVATE_FEED_USERNAME=VssSessionToken

# For fish (~/.config/fish/config.fish)
set -gx UV_KEYRING_PROVIDER subprocess
set -gx UV_INDEX_PRIVATE_FEED_USERNAME VssSessionToken

# For PowerShell
$env:UV_KEYRING_PROVIDER = "subprocess"
$env:UV_INDEX_PRIVATE_FEED_USERNAME = "VssSessionToken"
```

#### 4. Azure Authentication

Ensure you're authenticated with Azure CLI:

```bash
az login
```

### Configuration

The setup process creates a `uv.toml` configuration file with your feeds:

```toml
[[index]]
name = "pypi"
url = "https://pypi.org/simple/"

[[index]]
name = "private-feed"
url = "https://pkgs.dev.azure.com/myorg/_packaging/myfeed/pypi/simple/"
```

### Status Monitoring

Check your Azure configuration at any time:

```bash
uvve azure-status
```

Example output:

```
Azure DevOps Configuration Status

✅ Config file: /Users/username/.config/uv/uv.toml
✅ Keyring provider: subprocess

Configured Azure Feeds (2):
  • pypi: https://pypi.org/simple/
  • private-feed: https://pkgs.dev.azure.com/myorg/_packaging/myfeed/pypi/simple/

Azure Environment Variables (1):
  • UV_INDEX_PRIVATE_FEED_USERNAME=VssSessionToken
```

### Installing Packages

Once configured, you can install packages from both PyPI and your private feed:

```bash
# Install from PyPI (works as normal)
uv pip install requests pandas

# Install from private feed (automatically authenticated)
uv pip install my-private-package

# Install specific version from private feed
uv pip install my-private-package==1.2.3
```

### Multiple Azure Feeds

You can configure multiple Azure DevOps feeds:

```bash
# Add a second feed
uvve setup-azure
  --feed-url "https://pkgs.dev.azure.com/myorg/_packaging/anotherfeed/pypi/simple/"
  --feed-name "second-feed"
```

Each feed gets its own environment variable:

```bash
export UV_INDEX_PRIVATE_FEED_USERNAME=VssSessionToken
export UV_INDEX_SECOND_FEED_USERNAME=VssSessionToken
```

### Troubleshooting

#### Authentication Issues

```bash
# Re-authenticate with Azure
az login

# Check your Azure account
az account show
```

#### Configuration Issues

```bash
# Check Azure status
uvve azure-status

# Verify environment variables
echo $UV_KEYRING_PROVIDER
echo $UV_INDEX_PRIVATE_FEED_USERNAME
```

#### Package Installation Issues

```bash
# Check if keyring packages are installed
uv pip list | grep keyring

# Verify uv configuration
cat ~/.config/uv/uv.toml
```

```bash
uvve --show-completion >> ~/.bashrc # for bash
**What you get with completion:**

- ✅ Command completion (`uvve <TAB>` shows available commands)
- ✅ Subcommand completion (`uvve python <TAB>` shows `install`, `list`)
- ✅ Environment name completion (`uvve activate <TAB>` shows your environments)
- ✅ Option completion (`uvve --<TAB>` shows available options)

## Lockfile Format

uvve uses TOML lockfiles for reproducible environments:

```toml
[uvve]
version = "0.1.0"
generated = "2023-12-01T12:00:00"

[environment]
name = "myproject"
python_version = "3.11.0"

dependencies = [
    "requests==2.31.0",
    "click==8.1.7",
    # ... other packages
]

[metadata]
locked_at = "2023-12-01T12:00:00"
platform = { system = "Darwin", machine = "arm64" }
````

## Development

### Setup

```bash
git clone https://github.com/mgale694/uvve.git
cd uvve
uv pip install -e ".[dev]"
```

### Testing

```bash
pytest tests/
```

### Linting

```bash
ruff check src/ tests/
black src/ tests/
mypy src/
```

## Documentation

- 📖 [Complete Documentation](docs/index.md) - Comprehensive user guide
- 📊 [Rich Metadata & Analytics](docs/analytics.md) - Usage tracking and environment insights
- 🏗️ [Design Principles](docs/principles.md) - Core principles and architecture
- 🗺️ [Roadmap](docs/roadmap.md) - Future plans and development phases
- 📐 [Design Document](docs/design.md) - Technical design and implementation details

## Roadmap

uvve follows a phased development approach:

### ✅ Phase 1: MVP (Complete)

- Core environment management (`create`, `list`, `activate`, `remove`)
- Python version integration with uv
- Lockfile support (`lock`, `thaw`) with TOML format
- Cross-platform shell integration
- Rich CLI with beautiful output

### 🚀 Phase 2: Enhanced Features (In Progress)

- Advanced shell completions and auto-installation
- Rich metadata and environment templates
- Usage analytics and cleanup automation
- Environment sync and bulk operations

### 🌟 Phase 3: Ecosystem Integration (Planned)

- Homebrew formula and package manager distribution
- Global hooks with `.uvve-version` files
- Project linking and workspace isolation
- IDE integrations (VS Code, PyCharm)

### 🔗 Phase 4: uv Ecosystem Integration (Future)

- Deep integration with uv project workflows
- Shared configuration and unified developer experience
- `uv.lock` linking and project synchronization

### 🦀 Phase 5: Rust Evolution (Consideration)

- Performance optimization with Rust rewrite
- Static binary distribution
- Ecosystem alignment with uv's technology stack

See the [full roadmap](docs/roadmap.md) for detailed timelines and features.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [uv](https://github.com/astral-sh/uv) - The fast Python package installer and resolver
- [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) - Inspiration for the interface
