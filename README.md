# Update Apex Commit ID

This project contains a script to automatically update Apex commit IDs in PyTorch's `related_commits` file and create pull requests.

## Overview

The script performs the following operations:
1. **Branch Management**: Checkout specific branches in PyTorch and Apex repositories
2. **Commit Analysis**: Analyze Apex commits between the current PyTorch version and latest Apex
3. **File Updates**: Update the `related_commits` file with new Apex commit IDs
4. **PR Creation**: Create branches, commit changes, and optionally create GitHub PRs
5. **Browser Automation**: Automatically open browser with pre-filled PR forms

## Prerequisites

- Python 3.6+
- Git repositories:
  - PyTorch repository (local path: `../sriram-pytorch/pytorch`)
  - Apex repository (local path: `../apex`)
- GitHub CLI (optional, for automatic PR creation)

## Usage

### Basic Analysis (No Changes)
```bash
python3 pr_creation_script.py --pytorch-branch release/2.8 --apex-branch release/1.8.0
```

### Create Branch and Commit Only
```bash
python3 pr_creation_script.py --pytorch-branch release/2.8 --apex-branch release/1.8.0 --create-pr-branch
```

### Complete Automation (Push + PR Creation)
```bash
python3 pr_creation_script.py --pytorch-branch release/2.8 --apex-branch release/1.8.0 --push-and-create-pr
```

### Complete Automation with Browser Opening
```bash
python3 pr_creation_script.py --pytorch-branch release/2.8 --apex-branch release/1.8.0 --pytorch-repo-url https://github.com/skkkumar/pytorch --push-and-create-pr --open-browser
```

## Parameters

- `--pytorch-branch`: PyTorch branch to checkout (e.g., `release/2.8`)
- `--apex-branch`: Apex branch to checkout (e.g., `release/1.8.0`)
- `--pytorch-repo-url`: PyTorch repository URL (default: `https://github.com/ROCm/pytorch`)
- `--create-pr-branch`: Create new branch and commit changes
- `--push-and-create-pr`: Push branch and create GitHub PR
- `--open-browser`: Open browser with pre-filled PR form

## Features

### 🔄 Branch Management
- Automatic checkout of specified branches
- Handling of uncommitted changes with git stash
- Dynamic remote detection (upstream vs origin)

### 📊 Commit Analysis
- Detailed analysis of Apex commits between versions
- PR extraction and analysis from commit messages
- Fixes link extraction from PR descriptions

### 📝 File Updates
- Updates `related_commits` file with new Apex commit IDs
- Simulation mode for safe analysis without changes
- Merge conflict detection and reporting

### 🚀 PR Automation
- Automatic branch creation with proper naming
- Formatted commit messages with detailed descriptions
- Force push handling for existing branches
- GitHub CLI integration with fallback to manual instructions

### 🌐 Browser Integration
- Automatic browser opening with pre-filled PR forms
- URL encoding for proper GitHub integration
- Configurable repository URLs for different forks

## File Structure

```
update_apex_commit_id/
├── pr_creation_script.py    # Main script
└── README.md               # This file
```

## Output

The script provides detailed output including:
- Branch setup status
- Commit analysis results
- PR details and fixes links
- File update confirmations
- Git operation results
- PR creation URLs and instructions

## Error Handling

- Graceful handling of git conflicts
- Automatic force push for existing branches
- Fallback instructions when GitHub CLI is unavailable
- Detailed error messages and troubleshooting steps

## Examples

### Example 1: Analysis Only
```bash
python3 pr_creation_script.py --pytorch-branch release/2.8 --apex-branch release/1.8.0
```
**Output**: Detailed analysis of commits and PRs without making any changes.

### Example 2: Full Automation
```bash
python3 pr_creation_script.py \
  --pytorch-branch release/2.8 \
  --apex-branch release/1.8.0 \
  --pytorch-repo-url https://github.com/skkkumar/pytorch \
  --push-and-create-pr \
  --open-browser
```
**Output**: Complete automation from analysis to browser opening with pre-filled PR form.

## Troubleshooting

### Common Issues

1. **Git conflicts**: The script detects and reports merge conflicts without automatic resolution
2. **Push failures**: Automatically attempts force push for existing branches
3. **GitHub CLI not available**: Provides manual PR creation instructions
4. **Repository not found**: Verifies repository existence before operations

### Manual Steps

If automation fails, the script provides:
- Exact URLs to visit
- Pre-filled title and description
- Step-by-step manual instructions

## Contributing

This script is designed for updating Apex commit IDs in PyTorch repositories. For modifications:
1. Test in simulation mode first
2. Verify repository paths and URLs
3. Test with different branch combinations

## License

This project is part of the PyTorch development workflow. 