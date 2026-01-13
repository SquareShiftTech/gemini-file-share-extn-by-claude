"""
Google Cloud Storage client operations.
"""

import logging
import mimetypes
from typing import List, Optional

from google.cloud import storage
from google.cloud.exceptions import Conflict, NotFound, Forbidden
from google.api_core.exceptions import GoogleAPICallError

logger = logging.getLogger(__name__)


class GCSError(Exception):
    """Custom exception for GCS operations."""
    pass


class GCSClient:
    """Client for Google Cloud Storage operations."""

    DEFAULT_LOCATION = "US-EAST1"
    DEFAULT_STORAGE_CLASS = "STANDARD"

    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize the GCS client.

        Args:
            project_id: Optional GCP project ID. If not provided, uses default.
        """
        try:
            self._client = storage.Client(project=project_id)
            self._project_id = self._client.project
        except Exception as e:
            raise GCSError(f"Failed to initialize GCS client: {e}")

    @property
    def project_id(self) -> str:
        """Get the current project ID."""
        return self._project_id

    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Check if a bucket exists.

        Args:
            bucket_name: Name of the bucket to check

        Returns:
            True if bucket exists, False otherwise
        """
        bucket = self._client.bucket(bucket_name)
        return bucket.exists()

    def ensure_bucket_exists(
        self,
        bucket_name: str,
        location: Optional[str] = None,
        storage_class: Optional[str] = None,
    ) -> bool:
        """
        Ensure a bucket exists, creating it if necessary.

        Args:
            bucket_name: Name of the bucket
            location: Location for the bucket (default: US-EAST1)
            storage_class: Storage class (default: STANDARD)

        Returns:
            True if bucket was created, False if it already existed

        Raises:
            GCSError: If bucket creation fails
        """
        location = location or self.DEFAULT_LOCATION
        storage_class = storage_class or self.DEFAULT_STORAGE_CLASS

        bucket = self._client.bucket(bucket_name)

        if bucket.exists():
            logger.info(f"Bucket {bucket_name} already exists")
            return False

        try:
            bucket.iam_configuration.uniform_bucket_level_access_enabled = True
            bucket.storage_class = storage_class

            new_bucket = self._client.create_bucket(
                bucket,
                location=location,
            )
            logger.info(f"Created bucket {new_bucket.name} in {location}")
            return True

        except Conflict:
            logger.warning(f"Bucket {bucket_name} already exists (conflict)")
            return False

        except Forbidden as e:
            raise GCSError(
                f"Permission denied creating bucket {bucket_name}. "
                f"Ensure you have storage.buckets.create permission. Error: {e}"
            )

        except GoogleAPICallError as e:
            raise GCSError(f"Failed to create bucket {bucket_name}: {e}")

    def upload_file(
        self,
        bucket_name: str,
        source_file_path: str,
        destination_blob_name: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload a file to a GCS bucket.

        Args:
            bucket_name: Name of the target bucket
            source_file_path: Path to the local file
            destination_blob_name: Name for the blob in GCS
            content_type: Optional MIME type (auto-detected if not provided)

        Returns:
            The name of the uploaded blob

        Raises:
            GCSError: If upload fails
        """
        try:
            bucket = self._client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)

            if content_type is None:
                content_type, _ = mimetypes.guess_type(source_file_path)
                if content_type is None:
                    content_type = "application/octet-stream"

            blob.upload_from_filename(
                source_file_path,
                content_type=content_type,
            )

            logger.info(
                f"Uploaded {source_file_path} to gs://{bucket_name}/{destination_blob_name}"
            )
            return destination_blob_name

        except NotFound:
            raise GCSError(f"Bucket {bucket_name} not found")

        except Forbidden as e:
            raise GCSError(
                f"Permission denied uploading to {bucket_name}. "
                f"Ensure you have storage.objects.create permission. Error: {e}"
            )

        except GoogleAPICallError as e:
            raise GCSError(f"Failed to upload file: {e}")

    def make_object_public(self, bucket_name: str, blob_name: str) -> str:
        """
        Make an object publicly accessible.

        This uses IAM policies to grant allUsers read access.
        Requires uniform bucket-level access to be enabled.

        Args:
            bucket_name: Name of the bucket
            blob_name: Name of the blob to make public

        Returns:
            The public URL of the object

        Raises:
            GCSError: If making public fails
        """
        try:
            bucket = self._client.bucket(bucket_name)

            bucket.reload()
            if not bucket.iam_configuration.uniform_bucket_level_access_enabled:
                bucket.iam_configuration.uniform_bucket_level_access_enabled = True
                bucket.patch()
                logger.info(f"Enabled uniform bucket-level access for {bucket_name}")

            policy = bucket.get_iam_policy(requested_policy_version=3)

            binding_exists = False
            for binding in policy.bindings:
                if binding["role"] == "roles/storage.objectViewer":
                    if "allUsers" in binding["members"]:
                        binding_exists = True
                        break

            if not binding_exists:
                policy.bindings.append({
                    "role": "roles/storage.objectViewer",
                    "members": ["allUsers"],
                })
                bucket.set_iam_policy(policy)
                logger.info(f"Made bucket {bucket_name} publicly readable")

            public_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
            return public_url

        except Forbidden as e:
            raise GCSError(
                f"Permission denied setting public access on {bucket_name}. "
                f"Ensure you have storage.buckets.setIamPolicy permission. "
                f"Note: Public access may be blocked by organization policy. Error: {e}"
            )

        except GoogleAPICallError as e:
            raise GCSError(f"Failed to make object public: {e}")

    def list_buckets(self) -> List[str]:
        """
        List all accessible buckets.

        Returns:
            List of bucket names

        Raises:
            GCSError: If listing fails
        """
        try:
            buckets = list(self._client.list_buckets())
            return [bucket.name for bucket in buckets]

        except Forbidden as e:
            raise GCSError(
                f"Permission denied listing buckets. "
                f"Ensure you have storage.buckets.list permission. Error: {e}"
            )

        except GoogleAPICallError as e:
            raise GCSError(f"Failed to list buckets: {e}")
