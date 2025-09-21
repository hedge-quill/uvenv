# Usage Analytics and Environment Insights

This document describes the analytics and usage tracking features in uvve that help you understand environment usage patterns and maintain clean, organized environments.

## Overview

uvve's analytics system provides insights into how your environments are used, helping you identify unused environments, track usage patterns, and make informed decisions about environment cleanup and organization.

## Analytics Commands

### `uvve analytics [name]`

Show analytics for a specific environment or summary for all environments.

**Examples:**

```bash
# Show analytics for specific environment
uvve analytics myproject

# Show summary for all environments
uvve analytics
```

**Sample Output (Specific Environment):**

```
Environment Analytics: myproject

📊 Usage Statistics
  Created:        2024-01-15 10:30:00
  Last Used:      2024-01-20 14:22:15 (5 days ago)
  Usage Count:    42 activations
  Frequency:      High (8.4 uses/day)

📝 Metadata
  Description:    Web API project for customer management
  Tags:          web, api, production
  Python:        3.11.5
  Size:          150.0 MB

🔍 Health Status
  Status:        🟢 Healthy
  Recommendation: Keep - actively used environment
```

**Sample Output (All Environments):**

```
Environment Analytics Summary

📈 Usage Overview
  Total Environments:     8
  Active Environments:    5
  Inactive (30+ days):    2
  Storage Used:          1.2 GB

🏆 Most Used Environments
  myapi          127 uses (last: 2 hours ago)
  webapp         89 uses  (last: 1 day ago)
  dataproj       45 uses  (last: 3 days ago)

⚠️  Cleanup Candidates
  oldproj        0 uses   (last: 45 days ago) - 180 MB
  testenv        2 uses   (last: 60 days ago) - 95 MB
```

### `uvve status`

Show environment utility overview with quick insights.

```bash
uvve status
```

**Sample Output:**

```
Environment Health Status

🟢 Healthy (5)
  myapi, webapp, dataproj, mlmodel, scripts

🟡 Warning (1)
  oldproj - Not used in 45 days (180 MB)

🔴 Attention Needed (2)
  testenv - Not used in 60 days (95 MB)
  broken  - Missing Python interpreter

💡 Recommendations
  • Run 'uvve cleanup --dry-run' to see cleanup options
  • Consider archiving unused environments
  • Total recoverable space: 275 MB
```

### `uvve cleanup`

Clean up unused environments automatically.

## Environment Cleanup

The cleanup system helps you maintain a clean environment directory by automatically identifying and removing unused environments.

### `uvve cleanup`

Automatically clean up unused environments based on usage patterns.

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

Edit environment metadata to improve organization and analytics.

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

The list command supports usage information and sorting.

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

## Usage Insights

## Analytics Insights

### Environment Utility Categories

The system automatically categorizes environments:

- 🟢 **Healthy**: Regular usage, active environment
- 🟡 **Warning**: Low usage (≤5 times) or unused 30-90 days
- 🔴 **Needs Attention**: Never used or unused 90+ days

### Analytics Metrics

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

### Tagging Strategy

Common tagging approaches:

- **Environment type**: `production`, `development`, `testing`, `experiment`
- **Project type**: `web`, `api`, `ml`, `data`, `cli`
- **Technology**: `django`, `flask`, `pytorch`, `pandas`
- **Criticality**: `critical`, `important`, `optional`

### Maintenance Workflow

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
uvve cleanup --unused-for 90 --interactive
```

### Organization Tips

1. **Set descriptions**: Use meaningful descriptions for better organization
2. **Use tags**: Tag environments by project type, status, or purpose
3. **Regular cleanup**: Review unused environments monthly
4. **Monitor usage**: Check analytics to understand your workflow patterns
5. **Set project roots**: Link environments to their source code directories

## Example Output

### Analytics Summary

```bash
$ uvve analytics

Environment Analytics Summary

📈 Usage Overview
  Total Environments:     8
  Active Environments:    5
  Inactive (30+ days):    2
  Storage Used:          1.2 GB

🏆 Most Used Environments
  myapi          127 uses (last: 2 hours ago)
  webapp         89 uses  (last: 1 day ago)
  dataproj       45 uses  (last: 3 days ago)

⚠️  Cleanup Candidates
  oldproj        0 uses   (last: 45 days ago) - 180 MB
  testenv        2 uses   (last: 60 days ago) - 95 MB
```

### Status Overview

```bash
$ uvve status

Environment Health Status

🟢 Healthy (5)
  myapi, webapp, dataproj, mlmodel, scripts

🟡 Warning (1)
  oldproj - Not used in 45 days (180 MB)

🔴 Attention Needed (2)
  testenv - Not used in 60 days (95 MB)
  broken  - Missing Python interpreter

💡 Recommendations
  • Run 'uvve cleanup --dry-run' to see cleanup options
  • Consider archiving unused environments
  • Total recoverable space: 275 MB
```
