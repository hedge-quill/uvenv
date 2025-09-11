# uvenv Design Document

## Overview

`uvenv` is designed as a lightweight wrapper around [uv](https://github.com/astral-sh/uv) for managing Python virtual environments. It provides a simple, pyenv-virtualenv-like interface while leveraging uv's speed and efficiency.

## Goals

1. **Simplicity**: Provide an intuitive CLI for common virtual environment operations
2. **Speed**: Leverage uv's fast Python installation and environment creation
3. **Reproducibility**: Support lockfiles for consistent environments across systems
4. **Shell Integration**: Easy activation/deactivation in various shells
5. **Metadata**: Track environment usage and metadata

## Architecture

### Core Components

```
uvenv/
├── cli.py              # CLI entrypoint using Typer
├── core/
│   ├── manager.py      # Environment management
│   ├── python.py       # Python version management
│   ├── paths.py        # Path utilities
│   ├── freeze.py       # Lockfile management
│   └── utils.py        # Utility functions
└── shell/
    ├── activate.py     # Activation script generation
    └── completion.py   # Shell completion
```

### Data Flow

1. **User Command** → CLI module parses command
2. **CLI** → Calls appropriate manager (Environment, Python, Freeze)
3. **Manager** → Uses PathManager for file operations
4. **Manager** → Calls uv subprocess for actual operations
5. **Manager** → Updates metadata and lockfiles
6. **CLI** → Returns formatted output to user

## Design Decisions

### Environment Storage

**Decision**: Store environments in `~/.uvenv/<name>/`

**Rationale**:

- Centralized location for easy management
- Follows convention of similar tools (pyenv, rbenv)
- Avoids project-specific .venv folders that can be accidentally committed

### Lockfile Format

**Decision**: Use TOML format for lockfiles

**Rationale**:

- Human-readable and editable
- Well-supported in Python ecosystem
- More structured than requirements.txt
- Allows for metadata storage

### Metadata Storage

**Decision**: Store metadata in JSON format alongside environments

**Rationale**:

- Track creation time, last used, activation status
- Enables future features like environment cleanup
- JSON is universally supported and lightweight

### CLI Framework

**Decision**: Use Typer for CLI

**Rationale**:

- Modern Python CLI framework
- Type hints and automatic validation
- Rich integration for beautiful output
- Automatic help generation

### Error Handling

**Decision**: Wrap uv subprocess calls with meaningful error messages

**Rationale**:

- uv errors can be cryptic for end users
- Provide context-specific error messages
- Graceful degradation when uv is not available

## File Structure

### Environment Directory Layout

```
~/.uvenv/<env_name>/
├── bin/                    # Python executable and scripts
│   ├── python              # Python interpreter
│   ├── pip                 # pip
│   └── activate            # Activation script
├── lib/python3.x/          # Python packages
├── uvenv.lock              # Lockfile (TOML)
└── uvenv.meta.json         # Metadata (JSON)
```

### Lockfile Schema

```toml
[uvenv]
version = "0.1.0"           # uvenv version that created this
generated = "ISO-8601"      # Generation timestamp

[environment]
name = "env_name"           # Environment name
python_version = "3.11.0"  # Exact Python version

dependencies = [            # Frozen package list
    "package==version",
    # ...
]

[metadata]
locked_at = "ISO-8601"      # Lock timestamp

[metadata.platform]        # Platform info for compatibility
system = "Darwin"           # OS
machine = "arm64"           # Architecture
python_implementation = "CPython"
```

### Metadata Schema

```json
{
  "name": "env_name",
  "python_version": "3.11.0",
  "created_at": "ISO-8601",
  "last_used": "ISO-8601",
  "active": false,
  "tags": ["project-x", "development"]
}
```

## Command Design

### Command Mapping

| uvenv command         | uv equivalent                         | Notes                          |
| --------------------- | ------------------------------------- | ------------------------------ |
| `python install 3.11` | `uv python install 3.11`              | Direct wrapper                 |
| `python list`         | `uv python list`                      | Enhanced with status table     |
| `create name 3.11`    | `uv venv ~/.uvenv/name --python 3.11` | Custom path                    |
| `activate name`       | N/A                                   | Generates shell script         |
| `list`                | N/A                                   | Custom implementation          |
| `remove name`         | N/A                                   | Custom implementation          |
| `lock name`           | N/A                                   | Uses pip freeze + metadata     |
| `thaw name`           | N/A                                   | Uses pip install from lockfile |

### Shell Integration Strategy

**Activation**:

1. Generate shell-specific activation commands
2. Support bash, zsh, fish, PowerShell
3. Return commands for eval, don't modify shell directly

**Completion**:

1. Provide completion scripts for each shell
2. Complete environment names for relevant commands
3. Easy installation instructions

## Implementation Phases

### Phase 1: Core Functionality

- [x] Basic CLI structure with Typer
- [x] Environment creation/removal
- [x] Environment listing
- [x] Path management
- [x] Basic activation script generation

### Phase 2: Lockfile Support

- [x] Lock command (freeze current state)
- [x] Thaw command (restore from lockfile)
- [x] TOML lockfile format
- [x] Metadata tracking

### Phase 3: Enhanced Features

- [ ] Shell completion scripts
- [ ] Environment templates
- [ ] Automatic cleanup of old environments
- [ ] Enhanced shell integration
- [ ] Configuration file support

### Phase 4: Advanced Features

- [ ] Environment tagging
- [ ] Usage analytics
- [ ] Integration with project files (pyproject.toml)
- [ ] Environment sharing/export
- [ ] Plugin system

## Testing Strategy

### Unit Tests

- Test each core module independently
- Mock uv subprocess calls
- Test error conditions and edge cases

### Integration Tests

- Test complete workflows
- Test with actual uv installation
- Test across different platforms

### CLI Tests

- Test all command combinations
- Test help text and error messages
- Test shell script generation

## Security Considerations

1. **Path Validation**: Validate environment names to prevent path traversal
2. **Shell Injection**: Sanitize shell commands and arguments
3. **File Permissions**: Ensure proper permissions on created files/directories
4. **Subprocess Safety**: Use secure subprocess invocation patterns

## Performance Considerations

1. **Lazy Loading**: Only load modules when needed
2. **Caching**: Cache environment lists and metadata
3. **Parallel Operations**: Support parallel environment operations where safe
4. **Minimal Dependencies**: Keep dependency tree small for fast startup

## Future Enhancements

1. **Web Interface**: Optional web UI for environment management
2. **IDE Integration**: Extensions for VS Code, PyCharm
3. **Docker Integration**: Generate Dockerfiles from environments
4. **CI/CD Integration**: GitHub Actions, GitLab CI templates
5. **Environment Sharing**: Share environments across teams/projects
