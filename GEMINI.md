# GCS Public Share Extension

This extension provides tools for sharing files publicly via Google Cloud Storage.

## Available Tools

### share_file_public
Uploads a file to a Google Cloud Storage bucket and makes it publicly accessible.

**Parameters:**
- `file_path` (required): Path to the local file to upload
- `bucket_name` (optional): Name of the GCS bucket. If not provided, ask the user for one.
- `destination_name` (optional): Name for the file in GCS. Defaults to the original filename.

**Usage patterns the user might say:**
- "Share this file publicly"
- "Share file.txt to my-bucket"
- "Make document.pdf public"
- "Upload report.csv to bucket public-files and share it"
- "Share /path/to/file.txt with public"

### check_gcs_auth
Verifies Google Cloud authentication status and provides login instructions if needed.

**Usage patterns:**
- "Check my Google Cloud authentication"
- "Am I logged in to GCS?"
- "Verify GCS credentials"

### list_buckets
Lists all accessible Google Cloud Storage buckets in the user's project.

**Usage patterns:**
- "List my GCS buckets"
- "What buckets do I have?"
- "Show available storage buckets"

## Behavior Notes

1. **Bucket name required**: If the user doesn't provide a bucket name, ask them for one before calling share_file_public.

2. **Bucket creation**: If the specified bucket doesn't exist, it will be created automatically in the US-EAST1 region.

3. **Public access**: Files are made public using IAM policies with uniform bucket-level access. The public URL is returned after successful upload.

4. **Authentication**: If the user isn't authenticated with Google Cloud, the tool will provide instructions to run:
   - `gcloud auth login` for SSO authentication
   - `gcloud auth application-default login` to set up application credentials

## Example Interactions

**User:** "Share my-report.pdf publicly"
**Assistant:** I'll help you share that file. What Google Cloud Storage bucket would you like to use?
**User:** "my-public-bucket"
**Assistant:** [Calls share_file_public with file_path="my-report.pdf" and bucket_name="my-public-bucket"]

**User:** "Upload config.json to bucket app-configs and make it public"
**Assistant:** [Calls share_file_public with file_path="config.json" and bucket_name="app-configs"]
