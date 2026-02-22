#!/usr/bin/env python3
"""Release script for AI Governance Tool."""

import os
import re
import subprocess
from pathlib import Path
import argparse

def get_current_version():
    """Get current version from version.py."""
    version_file = Path("ai_governance_tool/version.py")
    with open(version_file) as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        return match.group(1) if match else None

def update_version(new_version):
    """Update version in version.py."""
    version_file = Path("ai_governance_tool/version.py")
    with open(version_file) as f:
        content = f.read()

    content = re.sub(
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        f'__version__ = "{new_version}"',
        content
    )

    with open(version_file, 'w') as f:
        f.write(content)

def create_release(version, dry_run=False):
    """Create a new release."""
    current = get_current_version()
    if current == version:
        print(f"Version {version} is already set")
        return

    # Update version
    update_version(version)

    if dry_run:
        print(f"Would create release v{version}")
        return

    # Create commit
    subprocess.run(['git', 'add', 'ai_governance_tool/version.py'], check=True)
    subprocess.run(['git', 'commit', '-m', f'chore: Bump version to {version}'], check=True)

    # Create and push tag
    subprocess.run(['git', 'tag', '-a', f'v{version}', '-m', f'Release v{version}'], check=True)
    subprocess.run(['git', 'push', 'origin', 'main', '--tags'], check=True)

def main():
    parser = argparse.ArgumentParser(description='Create a new release')
    parser.add_argument('version', help='New version number (e.g., 1.0.1)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    args = parser.parse_args()

    try:
        create_release(args.version, args.dry_run)
    except subprocess.CalledProcessError as e:
        print(f"Error creating release: {e}")
        exit(1)

if __name__ == '__main__':
    main()