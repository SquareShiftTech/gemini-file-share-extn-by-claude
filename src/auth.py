"""
Google Cloud authentication handling.
"""

import logging
import subprocess
import sys
from typing import Optional, Tuple

import google.auth
from google.auth.exceptions import DefaultCredentialsError

logger = logging.getLogger(__name__)


def check_authentication() -> Tuple[bool, Optional[str], str]:
    """
    Check if the user is authenticated with Google Cloud.

    Returns:
        Tuple of (is_authenticated, project_id, message)
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        if credentials and credentials.valid:
            return True, project, "Already authenticated"

        if credentials:
            try:
                from google.auth.transport.requests import Request
                credentials.refresh(Request())
                return True, project, "Credentials refreshed"
            except Exception as e:
                logger.warning(f"Failed to refresh credentials: {e}")

        return False, None, "Credentials exist but are not valid"

    except DefaultCredentialsError:
        return False, None, "No valid credentials found"

    except Exception as e:
        logger.exception("Error checking authentication")
        return False, None, f"Authentication check failed: {e}"


def is_gcloud_installed() -> bool:
    """Check if gcloud CLI is installed and accessible."""
    try:
        result = subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_gcloud_account() -> Optional[str]:
    """Get the currently active gcloud account."""
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "account"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            account = result.stdout.strip()
            return account if account else None
        return None
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def initiate_gcloud_login() -> dict:
    """
    Initiate gcloud authentication.

    This function checks if gcloud is installed and provides instructions
    for authentication. For interactive SSO login, it returns the command
    the user needs to run.

    Returns:
        Dictionary with login status and instructions
    """
    if not is_gcloud_installed():
        return {
            "success": False,
            "message": (
                "Google Cloud SDK (gcloud) is not installed. "
                "Please install it from: https://cloud.google.com/sdk/docs/install"
            ),
            "action_required": "install_gcloud",
        }

    account = get_gcloud_account()
    if account:
        return {
            "success": False,
            "message": (
                f"You are logged into gcloud as {account}, but application default "
                f"credentials may not be configured. Please run:\n"
                f"  gcloud auth application-default login\n"
                f"This will set up credentials for this application."
            ),
            "action_required": "run_adc_login",
            "command": "gcloud auth application-default login",
        }

    return {
        "success": False,
        "message": (
            "You are not authenticated with Google Cloud. Please run:\n"
            "  gcloud auth login\n"
            "This will open a browser for SSO authentication.\n\n"
            "After logging in, also run:\n"
            "  gcloud auth application-default login\n"
            "to set up application credentials."
        ),
        "action_required": "run_login",
        "command": "gcloud auth login && gcloud auth application-default login",
    }


def run_gcloud_auth_login() -> dict:
    """
    Attempt to run gcloud auth login interactively.

    Note: This may not work in all terminal environments.
    The MCP server typically runs as a subprocess without TTY access.

    Returns:
        Dictionary with the result of the login attempt
    """
    try:
        if not sys.stdin.isatty():
            return {
                "success": False,
                "message": (
                    "Cannot run interactive login from this context. "
                    "Please run 'gcloud auth login' in your terminal manually."
                ),
                "action_required": "manual_login",
                "command": "gcloud auth login",
            }

        result = subprocess.run(
            ["gcloud", "auth", "login"],
            timeout=300,
        )

        if result.returncode == 0:
            adc_result = subprocess.run(
                ["gcloud", "auth", "application-default", "login"],
                timeout=300,
            )

            if adc_result.returncode == 0:
                return {
                    "success": True,
                    "message": "Successfully authenticated with Google Cloud",
                }
            else:
                return {
                    "success": False,
                    "message": (
                        "Logged in to gcloud but failed to set up application "
                        "default credentials. Please run: "
                        "gcloud auth application-default login"
                    ),
                }
        else:
            return {
                "success": False,
                "message": "Login cancelled or failed",
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "Login timed out after 5 minutes",
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Login failed: {e}",
        }
