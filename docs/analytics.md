# Rich Metadata and Usage Analytics

This document describes the enhanced metadata system and usage analytics features added to uvve.

## Overview

uvve now includes a comprehensive metadata system that tracks environment usage patterns, descriptions, tags, and other information. This enables powerful analytics and cleanup automation features.

## Rich Metadata Features

### Enhanced Environment Creation

When creating environments, you can now provide rich metadata directly:

```bash
# Create with description and tags
uvve create myapi 3.11 --description "Customer API service" --add-tag production --add-tag api

# Interactive mode when no metadata provided
uvve create webapp 3.11
# Prompts for:
# Description (optional, press Enter to skip): My web application
# Add tags (optional):
# Press Enter after each tag, or just press Enter to finish
# Tag: web
# Tag: frontend
# Tag: [Enter to finish]
```

**Command Options:**

- `--description`, `-d`: Set environment description
- `--add-tag`, `-t`: Add a tag (can be used multiple times)
- Interactive prompts appear automatically when no metadata is provided

### Enhanced Metadata Schema

Each environment now stores rich metadata in `uvve.meta.json`:

```json
{
  "name": "myproject",
  "description": "Web API project for customer management",
  "tags": ["web", "api", "production"],
  "python_version": "3.11.5",
  "created_at": "2024-01-15T10:30:00Z",
  "last_used": "2024-01-20T14:22:15Z",
  "usage_count": 42,
  "active": false,
  "project_root": "/Users/alice/projects/web-api",
  "size_bytes": 157286400
}
```

### Metadata Fields

- **name**: Environment name
- **description**: User-provided description
- **tags**: List of tags for categorization
- **python_version**: Python version used
- **created_at**: Creation timestamp (ISO 8601)
- **last_used**: Last activation timestamp (ISO 8601)
- **usage_count**: Number of times activated
- **active**: Whether currently active (for future use)
- **project_root**: Associated project directory
- **size_bytes**: Environment size in bytes (calculated on demand)

## Usage Analytics Commands

### `uvve analytics [name]`

Show analytics for a specific environment or summary for all environments.

**Examples:**

```bash
# Show analytics for specific environment
uvve analytics myproject

# Show summary for all environments
uvve analytics
```

**Options:**

- `--detailed`, `-d`: Show detailed analytics (future feature)

### `uvve status`

Show environment utility overview with quick insights.

```bash
uvve status
```

This displays:

- Utility status for each environment (🟢 Active, 🟡 Warning, 🔴 Needs attention)
- Usage patterns and recommendations
- Summary of environments needing cleanup

### `uvve cleanup`

Clean up unused environments automatically.

```bash
# Preview what would be removed
uvve cleanup --dry-run

# Remove environments unused for 60+ days
uvve cleanup --unused-for 60

# Include low-usage environments (≤5 uses)
uvve cleanup --low-usage

# Interactive cleanup (ask for each environment)
uvve cleanup --interactive

# Force removal without confirmation
uvve cleanup --force
```

**Options:**

- `--dry-run`: Show what would be removed without actually removing
- `--unused-for DAYS`: Days since last use to consider unused (default: 30)
- `--low-usage`: Include environments with ≤5 total uses
- `--interactive`, `-i`: Ask before removing each environment
- `--force`, `-f`: Remove without confirmation

### `uvve edit <name>`

Edit environment metadata.

```bash
# Set description
uvve edit myproject --description "My web API project"

# Add tags
uvve edit myproject --add-tag "production"
uvve edit myproject --add-tag "api"

# Remove tags
uvve edit myproject --remove-tag "development"

# Set project root
uvve edit myproject --project-root ~/projects/web-api
```

**Options:**

- `--description`, `-d`: Set environment description
- `--add-tag`: Add a tag to the environment
- `--remove-tag`: Remove a tag from the environment
- `--project-root`: Set project root directory

### Enhanced `uvve list`

The list command now supports usage information and sorting.

```bash
# Show basic list
uvve list

# Show with usage statistics
uvve list --usage

# Sort by different criteria
uvve list --usage --sort-by usage     # Most used first
uvve list --usage --sort-by size      # Largest first
uvve list --usage --sort-by last_used # Most recently used first
```

**Options:**

- `--usage`, `-u`: Show usage statistics
- `--sort-by`: Sort by name, usage, size, or last_used

## Automatic Usage Tracking

Usage statistics are automatically updated when you activate environments:

```bash
# This automatically updates last_used and increments usage_count
uvve activate myproject
```

The system tracks:

- **Last used timestamp**: Updated on each activation
- **Usage count**: Incremented on each activation
- **Usage frequency**: Calculated as uses per day since creation

## Analytics Insights

### Environment Utility Categories

The system automatically categorizes environments:

- 🟢 **Healthy**: Regular usage, active environment
- 🟡 **Warning**: Low usage (≤5 times) or unused 30-90 days
- 🔴 **Needs Attention**: Never used or unused 90+ days

### Usage Patterns

Analytics include derived statistics:

- **Age**: Days since environment creation
- **Days since use**: Days since last activation
- **Usage frequency**: Average activations per day
- **Size efficiency**: Disk usage relative to activity level

### Cleanup Recommendations

The system identifies environments for potential cleanup:

- **Never used**: Created but never activated
- **Stale**: Not used for 30+ days (configurable)
- **Low usage**: Used ≤5 times total
- **Large unused**: High disk usage with low activity

## Examples

### Typical Workflow

```bash
# Create and set up environment
uvve create myproject 3.11
uvve edit myproject --description "Customer API service"
uvve edit myproject --add-tag "api" --add-tag "production"
uvve edit myproject --project-root ~/projects/customer-api

# Use environment (automatically tracked)
uvve activate myproject

# Review analytics
uvve analytics myproject
uvve status

# Periodic cleanup
uvve cleanup --dry-run
uvve cleanup --unused-for 60 --interactive
```

### Analytics Output Example

```bash
$ uvve analytics myproject

Analytics for 'myproject'

┌─────────────────┬────────────────────────────────────┐
│ Property        │ Value                              │
├─────────────────┼────────────────────────────────────┤
│ Name            │ myproject                          │
│ Python Version  │ 3.11.5                             │
│ Description     │ Customer API service               │
│ Tags            │ api, production                    │
│ Size            │ 245.7 MB                           │
└─────────────────┴────────────────────────────────────┘

┌──────────────────┬─────────────────┐
│ Metric           │ Value           │
├──────────────────┼─────────────────┤
│ Usage Count      │ 47              │
│ Last Used        │ 2024-01-20T...  │
│ Age (days)       │ 15              │
│ Days Since Use   │ 2               │
│ Usage Frequency  │ 3.133/day       │
└──────────────────┴─────────────────┘
```

### Status Output Example

```bash
$ uvve status

Environment Utility Overview

┌─────────────┬─────────────┬─────────────┬────────┬─────────────────────┐
│ Environment │ Last Used   │ Usage Count │ Size   │ Utility             │
├─────────────┼─────────────┼─────────────┼────────┼─────────────────────┤
│ myproject   │ 2d ago      │ 47          │ 246MB  │ 🟢 Healthy          │
│ experiment  │ 45d ago     │ 3           │ 150MB  │ 🟡 Unused (30+ days) │
│ old-test    │ Never       │ 0           │ 80MB   │ 🔴 Never used       │
└─────────────┴─────────────┴─────────────┴────────┴─────────────────────┘

💡 Found 2 unused environment(s). Consider running `uvve cleanup --dry-run` to review.
```

## Best Practices

### Environment Creation

```bash
# Production environments
uvve create prod-api 3.11 -d "Production API server" -t production -t api -t critical

# Development environments
uvve create dev-webapp 3.11 -d "Development web app" -t development -t web

# Experimental environments
uvve create ml-experiment 3.11 -d "Testing new ML model" -t experiment -t ml

# Quick environments (interactive mode)
uvve create temp-env 3.11
# Just press Enter to skip description and tags for temporary work
```

### Organizing with Tags

Common tagging strategies:

- **Environment type**: `production`, `development`, `testing`, `experiment`
- **Project type**: `web`, `api`, `ml`, `data`, `cli`
- **Technology**: `django`, `flask`, `pytorch`, `pandas`
- **Criticality**: `critical`, `important`, `optional`

### Workflow Integration

```bash
# Create project environment with metadata
uvve create customer-api 3.11 \
  --description "Customer management API service" \
  --add-tag production \
  --add-tag api \
  --add-tag django

# Check environment status periodically
uvve analytics customer-api

# Review all environments monthly
uvve status

# Clean up unused environments quarterly
uvve cleanup --older-than 90 --interactive
```

## Configuration

The analytics system uses sensible defaults but can be customized:

- **Unused threshold**: 30 days (configurable via `--unused-for`)
- **Low usage threshold**: 5 total uses (configurable via `--low-usage`)
- **Size calculation**: Includes all files in environment directory

## Best Practices

1. **Set descriptions**: Use meaningful descriptions for better organization
2. **Use tags**: Tag environments by project type, status, or purpose
3. **Regular cleanup**: Review unused environments monthly
4. **Monitor usage**: Check analytics to understand your workflow patterns
5. **Set project roots**: Link environments to their source code directories

## Future Enhancements

Planned features include:

- **Usage trends**: Historical usage patterns and graphs
- **Team analytics**: Share usage statistics across development teams
- **Integration hooks**: Automatic project linking via git repositories
- **Custom rules**: User-defined cleanup and categorization rules
- **Export functionality**: Export analytics data for external analysis
