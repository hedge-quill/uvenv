# uvve User Guide

## 📚 Documentation Navigation

- **[User Guide](index.md)** - Complete usage documentation (this page)
- **[Analytics & Insights](analytics.md)** - Usage tracking and environment analytics
- **[Design Principles](principles.md)** - Core principles and architecture decisions
- **[Roadmap](roadmap.md)** - Future development plans and phases
- **[Design Document](design.md)** - Technical implementation details

## Overview

This guide provides comprehensive documentation for `uvve`, a CLI tool for managing Python virtual environments using [uv](https://github.com/astral-sh/uv). For a quick overview and installation instructions, see the main [README](../README.md).

## Detailed Command Reference

### Python Version Management

#### `uvve python install <version>`

Install a Python version using uv.

**Arguments:**

- `version`: Python version to install (e.g., "3.11", "3.11.5")

**Examples:**

```bash
uvve python install 3.11.0
uvve python install 3.12        # Latest 3.12.x
```

#### `uvve python list`

List available and installed Python versions with detailed status information.

**Output:**

- ✓ Installed versions are marked with a checkmark
- Available versions show as "Available"
- Shows installation paths for installed versions

### Environment Management

#### `uvve create <name> <python_version> [OPTIONS]`

Create a new virtual environment with optional metadata.

**Arguments:**

- `name`: Name of the virtual environment
- `python_version`: Python version for the environment

**Options:**

- `--description`, `-d`: Set environment description
- `--add-tag`, `-t`: Add a tag (can be used multiple times)

**Examples:**

```bash
# Basic environment
uvve create myproject 3.11

# With metadata
uvve create myapi 3.11 --description "Customer API" --add-tag production --add-tag api

# Interactive metadata (prompts for description and tags)
uvve create webapp 3.11
```

#### Environment Activation

**Method 1: Shell Integration (Recommended)**

```bash
# Install shell integration (one-time setup)
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

### Lockfile Management

#### `uvve lock <name>`

Generate a comprehensive lockfile for the environment.

Creates a `uvve.lock` file containing:

- Environment name and Python version
- List of installed packages with exact versions
- Platform information for compatibility checking
- Generation timestamp for reproducibility auditing

#### `uvve thaw <name>`

Rebuild environment from lockfile with exact package versions.

**Process:**

1. Verifies Python version availability
2. Creates new environment
3. Installs exact package versions from lockfile
4. Restores metadata

### Enhanced Environment Management

#### `uvve list [OPTIONS]`

List environments with optional usage statistics and sorting.

**Options:**

- `--usage`, `-u`: Show usage statistics
- `--sort-by`: Sort by name, usage, size, or last_used

**Examples:**

```bash
uvve list                           # Basic list
uvve list --usage                   # With usage stats
uvve list --usage --sort-by usage   # Most used first
```

#### `uvve edit <name> [OPTIONS]`

Edit environment metadata after creation.

**Options:**

- `--description`, `-d`: Set environment description
- `--add-tag`: Add a tag to the environment
- `--remove-tag`: Remove a tag from the environment
- `--project-root`: Set project root directory

**Examples:**

```bash
uvve edit myproject --description "My web API project"
uvve edit myproject --add-tag "production"
uvve edit myproject --remove-tag "development"
```

### Analytics and Cleanup

#### `uvve analytics [name]`

Show detailed analytics for specific environment or summary for all environments.

**Examples:**

```bash
uvve analytics myproject    # Specific environment
uvve analytics             # All environments summary
```

#### `uvve status`

Show environment health overview with recommendations.

Displays:

- Health status (🟢 Healthy, 🟡 Warning, 🔴 Needs attention)
- Usage patterns and recommendations
- Summary of environments needing cleanup

#### `uvve cleanup [OPTIONS]`

Automatically clean up unused environments.

**Options:**

- `--dry-run`: Show what would be removed without removing
- `--unused-for DAYS`: Days since last use threshold (default: 30)
- `--low-usage`: Include environments with ≤5 total uses
- `--interactive`, `-i`: Ask before removing each environment
- `--force`, `-f`: Remove without confirmation

### Shell Integration

#### `uvve shell-integration [OPTIONS]`

Generate and install shell integration for automatic activation.

**Options:**

- `--shell`: Target shell (bash, zsh, fish, powershell)
- `--print`: Print integration script instead of installation instructions

**Examples:**

```bash
# Show installation instructions
uvve shell-integration

# Install directly to shell config
uvve shell-integration >> ~/.zshrc

# Generate for specific shell
uvve shell-integration --shell bash
```

## Complete Workflow Examples

### New Project Setup

```bash
# 1. Install shell integration (one-time setup)
uvve shell-integration >> ~/.zshrc && source ~/.zshrc

# 2. Install Python version
uvve python install 3.12.1

# 3. Create environment with metadata
uvve create myapi 3.12.1 \
  --description "Customer management API" \
  --add-tag production \
  --add-tag api

# 4. Activate environment
uvve activate myapi

# 5. Install packages
pip install fastapi uvicorn pydantic

# 6. Create lockfile for reproducibility
uvve lock myapi

# 7. Set project root for organization
uvve edit myapi --project-root ~/projects/customer-api
```

### Environment Maintenance

```bash
# Check environment health
uvve status

# View detailed analytics
uvve analytics myapi

# List environments with usage stats
uvve list --usage --sort-by last_used

# Clean up unused environments
uvve cleanup --unused-for 60 --interactive
```

### Sharing and Reproducibility

```bash
# Developer A creates environment and lockfile
uvve create sharedproject 3.11
# ... install packages ...
uvve lock sharedproject

# Developer B recreates exact environment
uvve thaw sharedproject
```

## Configuration and Storage

### Environment Storage Structure

```
~/.uvve/
├── myproject/
│   ├── bin/activate           # Activation script
│   ├── lib/python3.11/        # Python packages
│   ├── uvve.lock             # Lockfile (TOML format)
│   └── uvve.meta.json        # Metadata (usage, tags, description)
└── another-env/
    └── ...
```

### Lockfile Format

TOML format with comprehensive metadata:

```toml
[uvve]
version = "1.0.1"
generated = "2025-09-21T12:00:00"

[environment]
name = "myproject"
python_version = "3.11.5"

dependencies = [
    "requests==2.31.0",
    "click==8.1.7",
    # ... other packages
]

[metadata]
locked_at = "2025-09-21T12:00:00"

[metadata.platform]
system = "Darwin"
machine = "arm64"
python_implementation = "CPython"
```

## Best Practices

### Environment Organization

1. **Use descriptive names**: `customer-api` instead of `project1`
2. **Add meaningful descriptions**: Help identify project purpose
3. **Tag strategically**: Use tags for filtering and organization
4. **Set project roots**: Link environments to source code directories

### Reproducibility

1. **Always create lockfiles**: Ensure consistent environments
2. **Use specific Python versions**: Avoid compatibility issues
3. **Regular cleanup**: Maintain clean environment directory
4. **Document dependencies**: Use requirements files alongside lockfiles

### Tagging Strategy

Common patterns:

- **Environment type**: `production`, `development`, `testing`
- **Project type**: `web`, `api`, `ml`, `data`, `cli`
- **Technology stack**: `django`, `flask`, `pytorch`, `pandas`
- **Criticality**: `critical`, `important`, `experimental`

## Troubleshooting

### Common Issues

**uv not found:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Environment not activating:**

```bash
# Verify environment exists
uvve list

# Check activation command output
uvve activate myproject

# Recreate if corrupted
uvve remove myproject
uvve create myproject 3.11
```

**Lockfile restoration fails:**

```bash
# Check Python version availability
uvve python list

# Install required Python version
uvve python install 3.11

# Retry thaw operation
uvve thaw myproject
```

**Permission errors:**

```bash
# Ensure uvve directory is writable
chmod 755 ~/.uvve

# Check individual environment permissions
ls -la ~/.uvve/
```

## Advanced Features

### Shell Completion

Enable tab completion for commands and environment names:

```bash
# Auto-install for current shell
uvve --install-completion

# Manual installation
uvve --show-completion >> ~/.zshrc
```

### Environment Health Monitoring

Regular maintenance commands:

```bash
# Weekly: Check environment status
uvve status

# Monthly: Review usage analytics
uvve analytics

# Quarterly: Clean unused environments
uvve cleanup --unused-for 90 --interactive
```

### Integration with Development Tools

#### VS Code Integration

```bash
# Set Python interpreter to uvve environment
# Command Palette: Python: Select Interpreter
# Choose: ~/.uvve/myproject/bin/python
```

#### Git Integration

```bash
# Add to .gitignore
echo ".venv" >> .gitignore
echo "uvve.lock" >> .gitignore  # Optional: commit for reproducibility
```

For more technical details about uvve's architecture and design decisions, see the [Design Document](design.md).

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

Activate the environment (behavior depends on shell integration setup).

**Arguments:**

- `name`: Name of the virtual environment

**How it works:**

**Option 1: With Shell Integration (Recommended)**

```bash
# One-time setup:
uvve shell-integration >> ~/.zshrc && source ~/.zshrc

# Then activate directly:
uvve activate myproject
```

**Option 2: With eval (without shell integration)**

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

### Built-in Shell Integration (Recommended)

uvve provides built-in shell integration that makes activation seamless:

```bash
# One-time setup for your shell:
uvve shell-integration >> ~/.zshrc     # for zsh
uvve shell-integration >> ~/.bashrc    # for bash

# Restart your shell or source the config
source ~/.zshrc

# Now you can activate directly:
uvve activate myproject
```

### Manual Shell Functions (Alternative)

If you prefer custom functions, add to your shell config:

**Bash/Zsh:**

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

**Fish:**

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
