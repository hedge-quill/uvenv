# uvve Documentation

## 📚 Documentation Navigation

- **[User Guide](index.md)** - Complete usage documentation (this page)
- **[Rich Metadata & Analytics](analytics.md)** - Usage tracking and environment analytics
- **[Design Principles](principles.md)** - Core principles and architecture decisions
- **[Roadmap](roadmap.md)** - Future development plans and phases
- **[Design Document](design.md)** - Technical implementation details

## Overview

`uvve` is a CLI tool for managing Python virtual environments using [uv](https://github.com/astral-sh/uv). It provides a simple interface similar to `pyenv-virtualenv` but leverages the speed and efficiency of `uv`.

## Installation

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) installed and available in PATH

### Install uvve

```bash
pip install uvve
```

## Quick Start

### 1. Install shell integration (optional but recommended)

```bash
# Install shell integration for direct activation
uvve shell-integration --print >> ~/.zshrc  # for zsh
uvve shell-integration --print >> ~/.bashrc # for bash

# Restart your shell or source the config
source ~/.zshrc
```

### 2. Install a Python version

```bash
uvve python install 3.11
```

### 3. List available Python versions

```bash
uvve python list
```

### 4. Create a virtual environment

```bash
uvve create myproject 3.11
```

### 5. Activate the environment

**With shell integration (recommended):**

```bash
uvve activate myproject
```

**Without shell integration:**

```bash
eval "$(uvve activate myproject)"
```

### 6. List environments

```bash
uvve list
```

### 7. Create a lockfile

```bash
uvve lock myproject
```

### 8. Remove an environment

```bash
uvve remove myproject
```

## Commands

### Python Version Management

#### `uvve python install <version>`

Install a Python version using uv.

**Arguments:**

- `version`: Python version to install (e.g., "3.11", "3.11.5")

**Example:**

```bash
uvve python install 3.11.0
```

#### `uvve python list`

List available and installed Python versions.

**Example:**

```bash
uvve python list
```

**Output:**

- Shows a table with version names, installation status, and locations
- ✓ Installed versions are marked with a checkmark
- Available versions show as "Available"

#### `uvve python --help`

Show help for Python version management commands.

**Example:**

```bash
uvve python --help
```

### Environment Management

#### `uvve create <name> <python_version>`

Create a new virtual environment.

**Arguments:**

- `name`: Name of the virtual environment
- `python_version`: Python version for the environment

**Example:**

```bash
uvve create myproject 3.11
```

#### `uvve activate <name>`

Print shell activation snippet for the environment.

**Arguments:**

- `name`: Name of the virtual environment

**How it works:**

The `uvve activate` command doesn't directly activate the environment. Instead, it outputs the shell command needed to activate it. You have two options:

**Option 1: Use with `eval` (Recommended)**

```bash
eval "$(uvve activate myproject)"
```

This executes the activation command immediately and activates the environment in your current shell.

**Option 2: Manual execution**

```bash
# First, see what command to run:
uvve activate myproject
# Output: source /Users/username/.uvve/myproject/bin/activate

# Then manually execute the output:
source /Users/username/.uvve/myproject/bin/activate
```

**Why use `eval`?**

- ✅ Immediately activates the environment
- ✅ Works in shell functions and scripts
- ✅ Single command instead of two steps
- ✅ Consistent across different shells

**Example comparison:**

```bash
# Without eval - just shows the command:
$ uvve activate myproject
source /Users/mgale/.uvve/myproject/bin/activate

# With eval - actually activates:
$ eval "$(uvve activate myproject)"
(myproject) $ echo $VIRTUAL_ENV
/Users/mgale/.uvve/myproject
```

#### `uvve list`

List all virtual environments.

**Example:**

```bash
uvve list
```

#### `uvve remove <name>`

Remove a virtual environment.

**Arguments:**

- `name`: Name of the virtual environment

**Options:**

- `--force`, `-f`: Force removal without confirmation

**Example:**

```bash
uvve remove myproject
uvve remove myproject --force
```

### Lockfile Management

#### `uvve lock <name>`

Generate a lockfile for the environment.

**Arguments:**

- `name`: Name of the virtual environment

**Example:**

```bash
uvve lock myproject
```

This creates a `uvve.lock` file in the environment directory containing:

- Environment name and Python version
- List of installed packages with exact versions
- Platform information
- Generation timestamp

#### `uvve thaw <name>`

Rebuild environment from lockfile.

**Arguments:**

- `name`: Name of the virtual environment

**Example:**

```bash
uvve thaw myproject
```

### Shell Integration

#### `uvve shell-integration`

Generate and install shell integration for uvve.

This creates a shell function that wraps the `uvve` command to handle activation automatically without requiring `eval`.

**Options:**

- `--shell`: Target shell (bash, zsh, fish, powershell). Auto-detected if not specified
- `--print`: Print integration script instead of installation instructions

**Examples:**

```bash
# Show installation instructions for your shell
uvve shell-integration

# Install directly to your shell config
uvve shell-integration --print >> ~/.zshrc

# Generate for a specific shell
uvve shell-integration --shell bash

# Just print the script
uvve shell-integration --print
```

**After installation:**

- `uvve activate myenv` - Works directly without eval
- All other commands work normally
- Requires restarting your shell or sourcing the config

## Python Version Workflow Examples

### Installing and Managing Python Versions

```bash
# Check what Python versions are available
uvve python list

# Install a specific Python version
uvve python install 3.12.1

# Install multiple versions for different projects
uvve python install 3.11.7
uvve python install 3.10.13

# List all versions again to see installed ones
uvve python list
```

### Complete Project Setup Workflow

```bash
# 0. Optional: Install shell integration (one-time setup)
uvve shell-integration --print >> ~/.zshrc && source ~/.zshrc

# 1. Install the Python version you need
uvve python install 3.12.1

# 2. Create a virtual environment for your project
uvve create myproject 3.12.1

# 3. Activate the environment
# With shell integration:
uvve activate myproject
# Without shell integration:
# eval "$(uvve activate myproject)"

# 4. Install packages in your activated environment
pip install requests fastapi

# 5. Create a lockfile to save the exact environment state
uvve lock myproject

# 6. Later, recreate the environment from the lockfile
uvve thaw myproject
```

### Managing Multiple Projects

```bash
# Set up environments for different projects
uvve python install 3.11.7
uvve python install 3.12.1

uvve create api-project 3.12.1
uvve create legacy-project 3.11.7

# See all your environments
uvve list

# Switch between projects
# With shell integration:
uvve activate api-project
# ... work on api project

uvve activate legacy-project
# ... work on legacy project
```

## Configuration

### Environment Storage

By default, virtual environments are stored in `~/.uvve/`. Each environment is stored in its own directory:

```
~/.uvve/
├── myproject/
│   ├── bin/activate           # Activation script
│   ├── lib/python3.11/        # Python packages
│   ├── uvve.lock            # Lockfile
│   └── uvve.meta.json       # Metadata
└── another-env/
    ├── bin/activate
    ├── lib/python3.10/
    ├── uvve.lock
    └── uvve.meta.json
```

### Lockfile Format

The `uvve.lock` file is in TOML format:

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

[metadata.platform]
system = "Darwin"
machine = "arm64"
python_implementation = "CPython"
```

## Shell Integration

### Bash/Zsh

Add to your `.bashrc` or `.zshrc`:

```bash
# Function to activate uvve environments
uvactivate() {
    if [ -z "$1" ]; then
        echo "Usage: uvactivate <environment_name>"
        return 1
    fi
    eval "$(uvve activate "$1")"
}
```

### Fish

Add to your Fish config:

```fish
# Function to activate uvve environments
function uvactivate
    if test (count $argv) -eq 0
        echo "Usage: uvactivate <environment_name>"
        return 1
    end
    eval (uvve activate $argv[1])
end
```

## Best Practices

1. **Use lockfiles**: Always create lockfiles for reproducible environments
2. **Meaningful names**: Use descriptive environment names
3. **Clean up**: Remove unused environments regularly
4. **Version pinning**: Use specific Python versions for consistency

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/mgale694/uvve.git
cd uvve

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality

uvve uses modern Python tooling for code quality:

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type checking
mypy src/

# Run tests
pytest tests/

# Run pre-commit on all files
pre-commit run --all-files
```

### Pre-commit Hooks

The project includes pre-commit hooks for:

- Code formatting (black)
- Linting (ruff)
- Type checking (mypy)
- Standard checks (trailing whitespace, YAML/TOML validation)

## Troubleshooting

### Common Issues

**uv not found:**

```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Permission errors:**

```bash
# Ensure ~/.uvve is writable
chmod 755 ~/.uvve
```

**Environment not activating:**

```bash
# Check if environment exists
uvve list

# Recreate if necessary
uvve remove myproject
uvve create myproject 3.11
```
