#!/usr/bin/env python3
"""
GCS Public Share MCP Server for Gemini CLI.

This server exposes tools for uploading files to Google Cloud Storage
and making them publicly accessible.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from .auth import check_authentication, initiate_gcloud_login
from .gcs_client import GCSClient, GCSError
from .utils import validate_bucket_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="GCS Public Share",
    instructions="Share files publicly via Google Cloud Storage",
)

_gcs_client: Optional[GCSClient] = None


def get_gcs_client() -> GCSClient:
    """Get or create the GCS client instance."""
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = GCSClient()
    return _gcs_client


@mcp.tool
async def share_file_public(
    file_path: str,
    bucket_name: Optional[str] = None,
    destination_name: Optional[str] = None,
) -> dict:
    """
    Upload a file to Google Cloud Storage and make it publicly accessible.

    Args:
        file_path: Path to the local file to upload
        bucket_name: Name of the GCS bucket. If not provided, you must ask
                     the user for a bucket name.
        destination_name: Name for the file in GCS. Defaults to the original filename.

    Returns:
        A dictionary containing:
        - success: Boolean indicating if the operation succeeded
        - public_url: The public URL of the uploaded file (if successful)
        - message: Description of the result or error
        - bucket_name: The bucket used (for reference)
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return {
            "success": False,
            "message": f"File not found: {file_path}",
            "public_url": None,
            "bucket_name": None,
        }

    if not path.is_file():
        return {
            "success": False,
            "message": f"Path is not a file: {file_path}",
            "public_url": None,
            "bucket_name": None,
        }

    if not bucket_name:
        return {
            "success": False,
            "message": "Bucket name is required. Please ask the user for a Google Cloud Storage bucket name.",
            "needs_input": "bucket_name",
            "public_url": None,
            "bucket_name": None,
        }

    is_valid, error_msg = validate_bucket_name(bucket_name)
    if not is_valid:
        return {
            "success": False,
            "message": f"Invalid bucket name: {error_msg}",
            "public_url": None,
            "bucket_name": bucket_name,
        }

    auth_result = await check_gcs_auth()
    if not auth_result.get("authenticated"):
        return {
            "success": False,
            "message": auth_result.get("message", "Authentication required"),
            "needs_auth": True,
            "public_url": None,
            "bucket_name": bucket_name,
        }

    if destination_name is None:
        destination_name = path.name

    try:
        client = get_gcs_client()

        bucket_created = client.ensure_bucket_exists(bucket_name)
        if bucket_created:
            logger.info(f"Created new bucket: {bucket_name}")

        blob_name = client.upload_file(
            bucket_name=bucket_name,
            source_file_path=str(path),
            destination_blob_name=destination_name,
        )

        public_url = client.make_object_public(bucket_name, blob_name)

        return {
            "success": True,
            "message": f"File uploaded and made public successfully.",
            "public_url": public_url,
            "bucket_name": bucket_name,
            "blob_name": blob_name,
            "bucket_created": bucket_created,
        }

    except GCSError as e:
        logger.error(f"GCS operation failed: {e}")
        return {
            "success": False,
            "message": str(e),
            "public_url": None,
            "bucket_name": bucket_name,
        }
    except Exception as e:
        logger.exception("Unexpected error during file sharing")
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "public_url": None,
            "bucket_name": bucket_name,
        }


@mcp.tool
async def check_gcs_auth() -> dict:
    """
    Check Google Cloud authentication status and initiate login if needed.

    Returns:
        A dictionary containing:
        - authenticated: Boolean indicating if the user is authenticated
        - message: Description of the authentication status
        - project_id: The current GCP project (if authenticated)
    """
    try:
        is_auth, project_id, message = check_authentication()

        if is_auth:
            return {
                "authenticated": True,
                "message": f"Authenticated with Google Cloud. Project: {project_id}",
                "project_id": project_id,
            }
        else:
            login_result = initiate_gcloud_login()
            return {
                "authenticated": False,
                "message": login_result["message"],
                "action_required": login_result.get("action_required"),
                "command": login_result.get("command"),
            }

    except Exception as e:
        logger.exception("Error checking authentication")
        return {
            "authenticated": False,
            "message": f"Error checking authentication: {str(e)}",
        }


@mcp.tool
async def list_buckets() -> dict:
    """
    List all accessible Google Cloud Storage buckets.

    Returns:
        A dictionary containing:
        - success: Boolean indicating if the operation succeeded
        - buckets: List of bucket names (if successful)
        - message: Description of the result or error
    """
    auth_result = await check_gcs_auth()
    if not auth_result.get("authenticated"):
        return {
            "success": False,
            "buckets": [],
            "message": auth_result.get("message", "Authentication required"),
        }

    try:
        client = get_gcs_client()
        buckets = client.list_buckets()
        return {
            "success": True,
            "buckets": buckets,
            "message": f"Found {len(buckets)} bucket(s)",
        }
    except GCSError as e:
        return {
            "success": False,
            "buckets": [],
            "message": str(e),
        }


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
