# Rich Metadata and Usage Analytics

This document describes the enhanced metadata system and usage analytics features added to uvenv.

## Overview

uvenv now includes a comprehensive metadata system that tracks environment usage patterns, descriptions, tags, and other information. This enables powerful analytics and cleanup automation features.

## Rich Metadata Features

### Enhanced Environment Creation

When creating environments, you can now provide rich metadata directly:

```bash
# Create with description and tags
uvenv create myapi 3.11 --description "Customer API service" --add-tag production --add-tag api

# Interactive mode when no metadata provided
uvenv create webapp 3.11
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

Each environment now stores rich metadata in `uvenv.meta.json`:

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

### `uvenv analytics [name]`

Show analytics for a specific environment or summary for all environments.

**Examples:**

```bash
# Show analytics for specific environment
uvenv analytics myproject

# Show summary for all environments
uvenv analytics
```

**Options:**

- `--detailed`, `-d`: Show detailed analytics (future feature)

### `uvenv status`

Show environment health overview with quick insights.

```bash
uvenv status
```

This displays:

- Health status for each environment (🟢 Healthy, 🟡 Warning, 🔴 Needs attention)
- Usage patterns and recommendations
- Summary of environments needing cleanup

### `uvenv cleanup`

Clean up unused environments automatically.

```bash
# Preview what would be removed
uvenv cleanup --dry-run

# Remove environments unused for 60+ days
uvenv cleanup --unused-for 60

# Include low-usage environments (≤5 uses)
uvenv cleanup --low-usage

# Interactive cleanup (ask for each environment)
uvenv cleanup --interactive

# Force removal without confirmation
uvenv cleanup --force
```

**Options:**

- `--dry-run`: Show what would be removed without actually removing
- `--unused-for DAYS`: Days since last use to consider unused (default: 30)
- `--low-usage`: Include environments with ≤5 total uses
- `--interactive`, `-i`: Ask before removing each environment
- `--force`, `-f`: Remove without confirmation

### `uvenv edit <name>`

Edit environment metadata.

```bash
# Set description
uvenv edit myproject --description "My web API project"

# Add tags
uvenv edit myproject --add-tag "production"
uvenv edit myproject --add-tag "api"

# Remove tags
uvenv edit myproject --remove-tag "development"

# Set project root
uvenv edit myproject --project-root ~/projects/web-api
```

**Options:**

- `--description`, `-d`: Set environment description
- `--add-tag`: Add a tag to the environment
- `--remove-tag`: Remove a tag from the environment
- `--project-root`: Set project root directory

### Enhanced `uvenv list`

The list command now supports usage information and sorting.

```bash
# Show basic list
uvenv list

# Show with usage statistics
uvenv list --usage

# Sort by different criteria
uvenv list --usage --sort-by usage     # Most used first
uvenv list --usage --sort-by size      # Largest first
uvenv list --usage --sort-by last_used # Most recently used first
```

**Options:**

- `--usage`, `-u`: Show usage statistics
- `--sort-by`: Sort by name, usage, size, or last_used

## Automatic Usage Tracking

Usage statistics are automatically updated when you activate environments:

```bash
# This automatically updates last_used and increments usage_count
uvenv activate myproject
```

The system tracks:

- **Last used timestamp**: Updated on each activation
- **Usage count**: Incremented on each activation
- **Usage frequency**: Calculated as uses per day since creation

## Analytics Insights

### Environment Health Status

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
uvenv create myproject 3.11
uvenv edit myproject --description "Customer API service"
uvenv edit myproject --add-tag "api" --add-tag "production"
uvenv edit myproject --project-root ~/projects/customer-api

# Use environment (automatically tracked)
uvenv activate myproject

# Review analytics
uvenv analytics myproject
uvenv status

# Periodic cleanup
uvenv cleanup --dry-run
uvenv cleanup --unused-for 60 --interactive
```

### Analytics Output Example

```bash
$ uvenv analytics myproject

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
$ uvenv status

Environment Health Overview

┌─────────────┬─────────────┬─────────────┬────────┬─────────────────────┐
│ Environment │ Last Used   │ Usage Count │ Size   │ Health              │
├─────────────┼─────────────┼─────────────┼────────┼─────────────────────┤
│ myproject   │ 2d ago      │ 47          │ 246MB  │ 🟢 Healthy          │
│ experiment  │ 45d ago     │ 3           │ 150MB  │ 🟡 Unused (30+ days) │
│ old-test    │ Never       │ 0           │ 80MB   │ 🔴 Never used       │
└─────────────┴─────────────┴─────────────┴────────┴─────────────────────┘

💡 Found 2 unused environment(s). Consider running `uvenv cleanup --dry-run` to review.
```

## Best Practices

### Environment Creation

```bash
# Production environments
uvenv create prod-api 3.11 -d "Production API server" -t production -t api -t critical

# Development environments
uvenv create dev-webapp 3.11 -d "Development web app" -t development -t web

# Experimental environments
uvenv create ml-experiment 3.11 -d "Testing new ML model" -t experiment -t ml

# Quick environments (interactive mode)
uvenv create temp-env 3.11
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
uvenv create customer-api 3.11 \
  --description "Customer management API service" \
  --add-tag production \
  --add-tag api \
  --add-tag django

# Check environment status periodically
uvenv analytics customer-api

# Review all environments monthly
uvenv status

# Clean up unused environments quarterly
uvenv cleanup --older-than 90 --interactive
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
