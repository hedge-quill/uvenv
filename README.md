# uvenv

[![CI](https://github.com/mgale694/uvenv/workflows/CI/badge.svg)](https://github.com/mgale694/uvenv/actions)
[![PyPI version](https://badge.fury.io/py/uvenv.svg)](https://badge.fury.io/py/uvenv)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A CLI tool for managing Python virtual environments using [uv](https://github.com/astral-sh/uv). Think `pyenv-virtualenv` but powered by the speed of `uv`.

## Features

- 🚀 **Fast**: Leverages uv's speed for Python installation and environment creation
- 🎯 **Simple**: Intuitive CLI commands for common virtual environment operations
- 🔒 **Reproducible**: Lockfile support for consistent environments across systems
- 🐚 **Shell Integration**: Easy activation/deactivation in bash, zsh, fish, and PowerShell
- 📊 **Metadata**: Track environment usage and metadata

## Quick Start

### Installation

```bash
pip install uvenv
```

### Prerequisites

Ensure [uv](https://github.com/astral-sh/uv) is installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Basic Usage

```bash
# Install shell integration (one-time setup)
uvenv shell-integration >> ~/.zshrc && source ~/.zshrc

# Install a Python version
uvenv python install 3.11

# List available Python versions
uvenv python list

# Create a virtual environment
uvenv create myproject 3.11

# Activate the environment (with shell integration)
uvenv activate myproject

# List environments
uvenv list

# Create a lockfile
uvenv lock myproject

# Remove an environment
uvenv remove myproject
```

## Understanding Environment Activation

There are two ways to work with uvenv activation:

### Method 1: Direct Evaluation (Recommended)

```bash
eval "$(uvenv activate myproject)"
```

This **actually activates** the environment in your current shell session. The `eval` command executes the activation script that `uvenv activate` outputs.

### Method 2: Manual Activation

```bash
uvenv activate myproject
# Outputs: source /Users/username/.uvenv/myproject/bin/activate

# Then manually run the output:
source /Users/username/.uvenv/myproject/bin/activate
```

This **just shows** the activation command. You need to copy and run the output manually.

**Why use `eval`?**

- ✅ Activates the environment immediately
- ✅ Works in scripts and automation
- ✅ Single command instead of two steps
- ✅ No copy-pasting required

## Commands

| Command                          | Description                                     |
| -------------------------------- | ----------------------------------------------- |
| `uvenv python install <version>` | Install a Python version using uv               |
| `uvenv python list`              | List available and installed Python versions    |
| `uvenv create <name> <version>`  | Create a new virtual environment                |
| `uvenv activate <name>`          | Print shell activation snippet                  |
| `uvenv list`                     | List all virtual environments                   |
| `uvenv remove <name>`            | Remove a virtual environment                    |
| `uvenv lock <name>`              | Generate a lockfile for the environment         |
| `uvenv thaw <name>`              | Rebuild environment from lockfile               |
| `uvenv shell-integration`        | Install shell integration for direct activation |
| `uvenv --install-completion`     | Install tab completion for your shell           |
| `uvenv --show-completion`        | Show completion script for manual installation  |

## Environment Storage

Virtual environments are stored in `~/.uvenv/`:

```
~/.uvenv/
├── myproject/
│   ├── bin/activate           # Activation script
│   ├── lib/python3.11/        # Python packages
│   ├── uvenv.lock            # Lockfile (TOML format)
│   └── uvenv.meta.json       # Metadata
└── another-env/
    └── ...
```

## Shell Integration

### Option 1: Built-in Shell Integration (Recommended)

Install uvenv's shell integration to make `uvenv activate` work directly:

```bash
# Add shell integration to your shell config
uvenv shell-integration >> ~/.zshrc  # for zsh
uvenv shell-integration >> ~/.bashrc # for bash

# Restart your shell or source the config
source ~/.zshrc
```

**After installation, you can use:**

```bash
uvenv activate myproject    # No eval needed!
uvenv list                  # Works normally
uvenv python install 3.12  # Works normally
```

### Option 2: Manual Shell Functions

Add to your shell config for easier activation:

> **Note:** These functions use `eval "$(uvenv activate ...)"` to actually activate the environment, not just print the activation command.

### Bash/Zsh

```bash
# Add to ~/.bashrc or ~/.zshrc
uvactivate() {
    if [ -z "$1" ]; then
        echo "Usage: uvactivate <environment_name>"
        return 1
    fi
    eval "$(uvenv activate "$1")"
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
    eval (uvenv activate $argv[1])
end
```

## Shell Completion

uvenv supports tab completion for commands and arguments:

### Auto-Install Completion

```bash
# Install completion for your current shell
uvenv --install-completion

# Restart your terminal or source your shell config
```

### Manual Installation

If auto-install doesn't work, you can manually add completion:

```bash
# Show the completion script for your shell
uvenv --show-completion

# Add it to your shell config manually
uvenv --show-completion >> ~/.zshrc      # for zsh
uvenv --show-completion >> ~/.bashrc     # for bash
```

**What you get with completion:**

- ✅ Command completion (`uvenv <TAB>` shows available commands)
- ✅ Subcommand completion (`uvenv python <TAB>` shows `install`, `list`)
- ✅ Environment name completion (`uvenv activate <TAB>` shows your environments)
- ✅ Option completion (`uvenv --<TAB>` shows available options)

## Lockfile Format

uvenv uses TOML lockfiles for reproducible environments:

```toml
[uvenv]
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
```

## Development

### Setup

```bash
git clone https://github.com/mgale694/uvenv.git
cd uvenv
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
- 🏗️ [Design Principles](docs/principles.md) - Core principles and architecture
- 🗺️ [Roadmap](docs/roadmap.md) - Future plans and development phases
- 📐 [Design Document](docs/design.md) - Technical design and implementation details

## Roadmap

uvenv follows a phased development approach:

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
- Global hooks with `.uvenv-version` files
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
