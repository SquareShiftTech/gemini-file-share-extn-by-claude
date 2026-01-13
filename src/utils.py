"""
Utility functions for the GCS Public Share extension.
"""

import mimetypes
import os
import re
from pathlib import Path
from typing import Optional, Tuple


def validate_bucket_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a GCS bucket name according to Google's naming requirements.

    Bucket naming rules:
    - 3-63 characters long
    - Lowercase letters, numbers, hyphens, underscores, and dots
    - Must start and end with a letter or number
    - Cannot contain consecutive dots
    - Cannot be an IP address

    Args:
        name: The bucket name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Bucket name cannot be empty"

    if len(name) < 3:
        return False, "Bucket name must be at least 3 characters"

    if len(name) > 63:
        return False, "Bucket name cannot exceed 63 characters"

    if not re.match(r'^[a-z0-9]', name):
        return False, "Bucket name must start with a lowercase letter or number"

    if not re.match(r'.*[a-z0-9]$', name):
        return False, "Bucket name must end with a lowercase letter or number"

    if not re.match(r'^[a-z0-9][a-z0-9._-]*[a-z0-9]$', name) and len(name) > 2:
        return False, (
            "Bucket name can only contain lowercase letters, numbers, "
            "hyphens, underscores, and dots"
        )

    if '..' in name:
        return False, "Bucket name cannot contain consecutive dots"

    ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    if re.match(ip_pattern, name):
        return False, "Bucket name cannot be an IP address"

    return True, None


def expand_path(path: str) -> Path:
    """
    Expand a file path, handling ~ and environment variables.

    Args:
        path: The path to expand

    Returns:
        Expanded absolute Path object
    """
    expanded = os.path.expanduser(os.path.expandvars(path))
    return Path(expanded).resolve()


def get_content_type(file_path: str) -> str:
    """
    Get the MIME content type for a file.

    Args:
        file_path: Path to the file

    Returns:
        MIME type string
    """
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type or "application/octet-stream"


def format_file_size(size_bytes: int) -> str:
    """
    Format a file size in bytes to a human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
