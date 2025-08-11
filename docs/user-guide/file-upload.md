# File Upload Guide

This guide explains how to upload FASTQ files to Project Thalassa for SRS risk assessment analysis.

## File Requirements

### Supported Formats

- **File Type:** FASTQ format only (`.fastq` or `.fq`)
- **Compression:** Uncompressed files currently supported
- **Size Limit:** Maximum 100MB per file (configurable)
- **Encoding:** UTF-8 or ASCII

### Naming Convention

Files **MUST** follow this exact naming pattern:

```
PartnerID_CageID_YYYY-MM-DD_SampleID.fastq
```

#### Components Explained

| Component | Format | Example | Description |
|-----------|--------|---------|-------------|
| PartnerID | String | `Mowi` | Your organization identifier |
| CageID | String with hyphens | `CAGE-04B` | Unique cage/site identifier |
| YYYY-MM-DD | ISO date | `2025-08-15` | Sample collection date |
| SampleID | String | `S01` | Sample identifier within cage |

#### Valid Examples

✅ Correct naming:
- `Mowi_CAGE-04B_2025-08-15_S01.fastq`
- `SalMar_SITE-A-01_2025-12-03_Sample-001.fastq`
- `AquaGen_FARM-12_2025-11-20_SEQ-001.fastq`

❌ Invalid naming:
- `mowi_cage04b_08-15-2025_s01.fastq` (wrong date format)
- `Mowi-CAGE-04B-2025-08-15-S01.fastq` (wrong separator)
- `CAGE-04B_2025-08-15_S01.fastq` (missing PartnerID)

## Upload Methods

### Method 1: cURL Command Line

Basic upload:
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/Mowi_CAGE-04B_2025-08-15_S01.fastq" \
  http://localhost:8000/api/v1/upload
```

With progress bar:
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/file.fastq" \
  --progress-bar \
  http://localhost:8000/api/v1/upload
```

### Method 2: Python Script

```python
import requests
import os

def upload_fastq(file_path, api_url, token):
    """Upload a FASTQ file to Project Thalassa."""

    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Prepare request
    headers = {"Authorization": f"Bearer {token}"}

    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}

        # Upload file
        response = requests.post(
            f"{api_url}/api/v1/upload",
            headers=headers,
            files=files
        )

    # Check response
    if response.status_code == 200:
        print("Upload successful!")
        return response.json()
    else:
        print(f"Upload failed: {response.status_code}")
        print(response.json())
        return None

# Usage
if __name__ == "__main__":
    result = upload_fastq(
        file_path="Mowi_CAGE-04B_2025-08-15_S01.fastq",
        api_url="http://localhost:8000",
        token="YOUR_TOKEN_HERE"
    )
    print(result)
```

### Method 3: Bash Script

Create a reusable upload script:

```bash
#!/bin/bash
# save as: upload_fastq.sh

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
TOKEN="${BEARER_TOKEN:-YOUR_TOKEN_HERE}"

# Check arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <fastq_file>"
    exit 1
fi

FILE_PATH="$1"

# Validate file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File not found: $FILE_PATH"
    exit 1
fi

# Validate filename format
FILENAME=$(basename "$FILE_PATH")
if [[ ! "$FILENAME" =~ ^[A-Za-z0-9]+_[A-Za-z0-9-]+_[0-9]{4}-[0-9]{2}-[0-9]{2}_[A-Za-z0-9-]+\.fastq$ ]]; then
    echo "Error: Invalid filename format: $FILENAME"
    echo "Expected: PartnerID_CageID_YYYY-MM-DD_SampleID.fastq"
    exit 1
fi

# Upload file
echo "Uploading: $FILENAME"
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$FILE_PATH" \
    "$API_URL/api/v1/upload")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

# Check response
if [ "$http_code" -eq 200 ]; then
    echo "✓ Upload successful!"
    echo "$body" | python3 -m json.tool
else
    echo "✗ Upload failed (HTTP $http_code)"
    echo "$body"
    exit 1
fi
```

Usage:
```bash
chmod +x upload_fastq.sh
./upload_fastq.sh Mowi_CAGE-04B_2025-08-15_S01.fastq
```

### Method 4: Web Interface (Future)

A web-based upload interface is planned for future releases. Partners will be able to:
1. Log in with credentials
2. Drag and drop files
3. Monitor upload progress
4. View upload history

## Batch Uploads

### Sequential Upload

Upload multiple files one by one:

```bash
#!/bin/bash
for file in *.fastq; do
    echo "Uploading $file..."
    curl -X POST \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -F "file=@$file" \
        http://localhost:8000/api/v1/upload
    sleep 1  # Rate limiting
done
```

### Parallel Upload (Advanced)

Upload multiple files in parallel with GNU Parallel:

```bash
# Install GNU Parallel first
ls *.fastq | parallel -j 4 \
    'curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@{}" http://localhost:8000/api/v1/upload'
```

## Response Handling

### Successful Upload

```json
{
  "message": "File uploaded successfully",
  "filename": "Mowi_CAGE-04B_2025-08-15_S01.fastq",
  "file_path": "/uploads/Mowi_CAGE-04B_2025-08-15_S01.fastq",
  "metadata": {
    "partner_id": "Mowi",
    "cage_id": "CAGE-04B",
    "sample_date": "2025-08-15",
    "sample_id": "S01",
    "original_filename": "Mowi_CAGE-04B_2025-08-15_S01.fastq",
    "file_size": 2428613,
    "upload_time": "2025-08-11T12:30:45Z",
    "file_hash": "sha256:abc123..."
  }
}
```

### Error Responses

#### Invalid Filename (400)
```json
{
  "detail": "Invalid filename format. Expected: PartnerID_CageID_YYYY-MM-DD_SampleID.fastq"
}
```

#### Unauthorized (401)
```json
{
  "detail": "Not authenticated"
}
```

#### File Too Large (413)
```json
{
  "detail": "File size exceeds maximum limit of 100MB"
}
```

#### Server Error (500)
```json
{
  "detail": "Internal server error. Please try again later."
}
```

## Validation and Verification

### Pre-Upload Validation

Before uploading, validate your file:

```python
import re
from datetime import datetime

def validate_fastq_filename(filename):
    """Validate FASTQ filename format."""
    pattern = r'^([A-Za-z0-9]+)_([A-Za-z0-9-]+)_(\d{4}-\d{2}-\d{2})_([A-Za-z0-9-]+)\.fastq$'
    match = re.match(pattern, filename)

    if not match:
        return False, "Invalid format"

    partner_id, cage_id, date_str, sample_id = match.groups()

    # Validate date
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return False, "Invalid date"

    return True, {
        "partner_id": partner_id,
        "cage_id": cage_id,
        "sample_date": date_str,
        "sample_id": sample_id
    }

# Test validation
filename = "Mowi_CAGE-04B_2025-08-15_S01.fastq"
valid, result = validate_fastq_filename(filename)
if valid:
    print(f"✓ Valid filename: {result}")
else:
    print(f"✗ Invalid: {result}")
```

### Post-Upload Verification

Verify your upload was successful:

```bash
# List all uploaded files
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/upload/files

# Check specific file
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/upload/files?filename=Mowi_CAGE-04B_2025-08-15_S01.fastq"
```

## Troubleshooting

### Common Issues

#### "Invalid filename format"
- Check underscore separators (not hyphens or spaces)
- Verify date format is YYYY-MM-DD
- Ensure .fastq extension is lowercase
- Remove special characters from IDs

#### "File too large"
- Check file size: `ls -lh yourfile.fastq`
- Compress large files before upload (future feature)
- Contact admin to increase size limit if needed

#### "Authentication failed"
- Verify your Bearer token is correct
- Check token hasn't expired
- Ensure "Bearer " prefix is included
- No extra spaces in the header

#### "Connection refused"
- Verify the API server is running
- Check the API URL and port
- Ensure no firewall blocking
- Test with health endpoint first

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Verbose cURL
curl -v -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@file.fastq" \
  http://localhost:8000/api/v1/upload 2>&1

# Python with logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Validate Before Upload**: Check filename format and file size
2. **Use Batch Scripts**: For multiple files, automate with scripts
3. **Handle Errors Gracefully**: Implement retry logic for failures
4. **Monitor Progress**: Use progress indicators for large files
5. **Keep Records**: Log successful uploads with timestamps
6. **Secure Your Token**: Never share or commit tokens to version control
7. **Rate Limit Awareness**: Space out requests to avoid rate limiting

## Next Steps

After successful upload:
1. Files are automatically queued for analysis
2. Risk assessment processing begins
3. Results available in the dashboard within minutes
4. Email notification when analysis completes (if configured)

See the [Risk Assessment Guide](risk-assessment.md) for details on the analysis process.
