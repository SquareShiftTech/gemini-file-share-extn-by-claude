# GCS Public Share - Gemini CLI Extension

A Gemini CLI extension for sharing files publicly via Google Cloud Storage.

## Features

- **Share files publicly** - Upload files to GCS and make them accessible via public URL
- **Auto-create buckets** - Automatically creates buckets if they don't exist
- **Authentication handling** - Guides you through Google Cloud SSO authentication
- **List buckets** - View all your accessible GCS buckets

## Installation

### Option 1: Install from Release

1. Download the latest release for your platform from the [Releases page](https://github.com/SquareShiftTech/gemini-file-share-extn-by-claude/releases)

2. Extract the archive and install dependencies:
   ```bash
   cd gcs-public-share
   pip install -r requirements.txt
   # Or with uv:
   uv sync
   ```

3. Link the extension to Gemini CLI:
   ```bash
   gemini extensions link /path/to/gcs-public-share
   ```

### Option 2: Install from PyPI

```bash
pip install gcs-public-share
```

Then create the extension directory and link it:
```bash
# Clone or download the extension files
git clone https://github.com/SquareShiftTech/gemini-file-share-extn-by-claude.git
gemini extensions link /path/to/gcs-public-share
```

### Option 3: Install from Source

```bash
git clone https://github.com/SquareShiftTech/gemini-file-share-extn-by-claude.git
cd gcs-public-share
./scripts/install.sh
gemini extensions link .
```

## Prerequisites

- Python 3.10 or higher
- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli)

## Authentication

Before using the extension, authenticate with Google Cloud:

```bash
gcloud auth login
gcloud auth application-default login
```

## Usage

Once installed and authenticated, restart Gemini CLI and try these commands:

- **Share a file publicly:**
  ```
  Share /path/to/file.txt publicly
  ```

- **Share to a specific bucket:**
  ```
  Upload document.pdf to my-bucket and make it public
  ```

- **Check authentication status:**
  ```
  Check my Google Cloud authentication
  ```

- **List available buckets:**
  ```
  List my GCS buckets
  ```

## Available Tools

| Tool | Description |
|------|-------------|
| `share_file_public` | Upload a file to GCS and make it publicly accessible |
| `check_gcs_auth` | Check Google Cloud authentication status |
| `list_buckets` | List all accessible GCS buckets |

## Configuration

The extension uses your Google Cloud default project. To change the project:

```bash
gcloud config set project YOUR_PROJECT_ID
```

Buckets are created in the `US-EAST1` region by default with `STANDARD` storage class.

## Development

```bash
# Clone the repository
git clone https://github.com/SquareShiftTech/gemini-file-share-extn-by-claude.git
cd gcs-public-share

# Install dependencies
uv sync

# Run the MCP server directly (for testing)
uv run python -m src.server
```

## License

MIT License - see [LICENSE](LICENSE) for details.
