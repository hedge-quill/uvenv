# Design Principles

This document outlines the core design principles that guide the development of `uvve`.

## 🎯 Core Principles

### 1. Deterministic

**Principle**: Same lockfile = same environment, every time, everywhere.

**Implementation**:

- ✅ TOML lockfiles with exact package versions and hashes
- ✅ Platform metadata to detect compatibility issues
- ✅ Python version pinning in lockfiles
- ✅ Timestamp tracking for reproducibility auditing

**Verification**: `uvve thaw` with the same lockfile produces identical environments across machines.

### 2. Portable

**Principle**: Environments and lockfiles work seamlessly across different machines and platforms.

**Implementation**:

- ✅ Cross-platform path handling (Windows/Unix)
- ✅ Platform detection and metadata storage
- ✅ Shell-agnostic activation (bash/zsh/fish/PowerShell)
- ✅ Lockfiles include platform compatibility information

**Verification**: Lockfiles created on macOS work on Linux and Windows (with compatible packages).

### 3. Forward-Compatible

**Principle**: Lockfile format evolves gracefully without breaking existing environments.

**Implementation**:

- ✅ `uvve.version` metadata in lockfiles enables format evolution
- ✅ Structured TOML format allows adding new sections
- ✅ Graceful handling of unknown lockfile versions
- ✅ Backwards compatibility for metadata formats

**Verification**: Newer uvve versions can read and upgrade older lockfile formats.

### 4. Extensible

**Principle**: Architecture supports future enhancements without major rewrites.

**Implementation**:

- ✅ Modular core architecture (manager, python, freeze, paths)
- ✅ Plugin-ready shell integration system
- ✅ Metadata system supports custom fields
- ✅ TOML lockfiles can include new sections

**Future Extensions**:

- Multiple environments per project (like Poetry)
- Custom package sources and indices
- Environment templates and presets
- Integration with CI/CD systems

## 🔄 Workflow Principles

### Lock Workflow (`uvve lock`)

**Process**:

1. **Capture Python Version**: Use `uv python list --json` or equivalent
2. **Extract Dependencies**: Run `uv pip freeze` in the environment
3. **Collect Metadata**: Timestamp, uvve version, platform info
4. **Write Lockfile**: Store in `~/.uvve/<name>/uvve.lock`

**Guarantees**:

- ✅ Complete environment snapshot
- ✅ Reproducible dependency resolution
- ✅ Platform compatibility tracking

### Thaw Workflow (`uvve thaw`)

**Process**:

1. **Read Lockfile**: Parse TOML structure and validate format
2. **Verify Python**: Ensure correct Python version available (`uv python install` if needed)
3. **Create Environment**: Use `uv venv` with specified Python version
4. **Install Dependencies**: Use `uv pip install` with exact versions
5. **Verify Integrity**: Optional hash verification for security

**Guarantees**:

- ✅ Exact environment recreation
- ✅ Dependency integrity
- ✅ Platform compatibility warnings

### Sync Workflow (`uvve sync` - Future)

**Process**:

1. **Compare States**: Current environment vs lockfile
2. **Calculate Diff**: Missing, extra, or mismatched packages
3. **Minimal Updates**: Install/update only what's necessary
4. **Preserve User Changes**: Detect manual modifications

**Benefits**:

- Faster than full recreation
- Preserves development packages
- NPM-like incremental updates

## 🏗️ Architecture Principles

### Separation of Concerns

- **CLI Layer**: User interaction, command parsing, output formatting
- **Core Layer**: Business logic, environment management, Python handling
- **Shell Layer**: Platform-specific activation and completion
- **Storage Layer**: File system operations, path management

### Fail-Fast Philosophy

- ✅ Early validation of environment names and Python versions
- ✅ Immediate feedback on missing dependencies (uv)
- ✅ Clear error messages with actionable suggestions
- ✅ Graceful degradation when optional features unavailable

### Minimal External Dependencies

- ✅ Core functionality works with just `uv` and Python stdlib
- ✅ Rich/Typer for enhanced UX but not core functionality
- ✅ No heavy frameworks or complex dependency trees
- ✅ Fast startup times even on resource-constrained systems

## 🔐 Security Principles

### Safe Operations

- ✅ Path validation prevents directory traversal
- ✅ Subprocess calls use secure patterns
- ✅ No shell injection vulnerabilities
- ✅ Proper file permissions on created directories

### Integrity Verification

- ✅ Lockfiles include package hashes where available
- ✅ Metadata verification prevents tampering
- ✅ Optional signature verification (future)
- ✅ Secure defaults for file operations

## 📊 Performance Principles

### Leverage uv's Speed

- ✅ Delegate heavy operations to uv
- ✅ Minimal wrapper overhead
- ✅ Parallel operations where safe
- ✅ Efficient file I/O patterns

### Lazy Loading

- ✅ Load modules only when needed
- ✅ Cache expensive operations
- ✅ Minimize startup time
- ✅ Stream large outputs

## 🧪 Testing Principles

### Comprehensive Coverage

- ✅ Unit tests for all core modules
- ✅ Integration tests for workflows
- ✅ CLI tests for user interactions
- ✅ Cross-platform compatibility tests

### Realistic Scenarios

- ✅ Mock uv subprocess calls appropriately
- ✅ Test error conditions and edge cases
- ✅ Validate user-facing error messages
- ✅ Test upgrade and migration paths

## 🚀 Future Evolution

### Phase 1: MVP ✅

- Core environment management
- Basic lockfile support
- Shell integration
- Cross-platform compatibility

### Phase 2: Enhanced Features

- Advanced shell completions
- Environment templates
- Global hooks (.uvve-version files)
- Brew formula distribution

### Phase 3: Ecosystem Integration

- Project linking (`uvve link`)
- CI/CD integrations
- IDE plugins
- Community contributions

### Phase 4: Advanced Capabilities

- Rust rewrite consideration
- Static binary distribution
- Performance optimizations
- Enterprise features

## ✅ Principle Compliance Check

| Principle              | Status      | Implementation                                              |
| ---------------------- | ----------- | ----------------------------------------------------------- |
| **Deterministic**      | ✅ Complete | TOML lockfiles with versions, hashes, platform metadata     |
| **Portable**           | ✅ Complete | Cross-platform paths, shell detection, compatibility checks |
| **Forward-Compatible** | ✅ Complete | Versioned lockfile format, graceful degradation             |
| **Extensible**         | ✅ Complete | Modular architecture, plugin-ready design                   |
| **Secure**             | ✅ Complete | Input validation, safe subprocess calls, proper permissions |
| **Fast**               | ✅ Complete | uv delegation, lazy loading, minimal overhead               |
| **Testable**           | ✅ Complete | Comprehensive test suite, mocking, edge cases               |

All design principles are met in the current implementation! 🎯
