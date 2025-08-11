# Project Thalassa - Partner API Guide

Welcome to Project Thalassa's bioinformatics analysis platform. This guide will help you upload your sequence data files for SRS risk assessment analysis.

## Quick Start

To upload your data files, you'll need:
1. Your authentication token (provided separately)
2. A properly formatted `.fastq` file
3. A tool to make HTTP requests (like `cURL` or similar)

## Authentication

All API requests require a Bearer token in the Authorization header. Replace `YOUR_TOKEN_HERE` in the examples below with your actual authentication token.

```
Authorization: Bearer YOUR_TOKEN_HERE
```

## File Upload

### Endpoint Information

- **URL:** `https://api.thalassa.io/api/v1/upload` (Production) or `http://localhost:8000/api/v1/upload` (Development)
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Authentication:** Bearer token required

### File Naming Convention

**CRITICAL:** Your files must follow this exact naming pattern:

```
PartnerID_CageID_YYYY-MM-DD_SampleID.fastq
```

**Components:**
- `PartnerID`: Your organization identifier (e.g., "Mowi", "SalMar")
- `CageID`: Unique cage identifier (e.g., "CAGE-04B", "SITE-A-01")
- `YYYY-MM-DD`: Sample collection date in ISO format
- `SampleID`: Sample identifier within the cage (e.g., "S01", "Sample-001")

**Valid Examples:**
- `Mowi_CAGE-04B_2025-08-15_S01.fastq`
- `SalMar_SITE-A-01_2025-12-03_Sample-001.fastq`
- `AquaGen_FARM-12_2025-11-20_SEQ-001.fastq`

### Upload Using cURL

Here's how to upload a file using cURL:

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/your/Mowi_CAGE-04B_2025-08-15_S01.fastq" \
  https://api.thalassa.io/api/v1/upload
```

**Replace:**
- `YOUR_TOKEN_HERE` with your actual Bearer token
- `/path/to/your/` with the actual path to your file
- `Mowi_CAGE-04B_2025-08-15_S01.fastq` with your actual filename
- `api.thalassa.io` with localhost:8000 for local testing

### Successful Upload Response

When your file uploads successfully, you'll receive a response like this:

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
    "file_size": 1048576
  }
}
```

## Alternative Upload Methods

### Using PowerShell (Windows)

```powershell
$headers = @{
    "Authorization" = "Bearer YOUR_TOKEN_HERE"
}

$form = @{
    "file" = Get-Item "C:\path\to\your\Mowi_CAGE-04B_2025-08-15_S01.fastq"
}

Invoke-RestMethod -Uri "https://your-server-domain.com/api/v1/upload" -Method Post -Headers $headers -Form $form
```

### Using Python requests

```python
import requests

url = "https://your-server-domain.com/api/v1/upload"
headers = {
    "Authorization": "Bearer YOUR_TOKEN_HERE"
}

with open("Mowi_CAGE-04B_2025-08-15_S01.fastq", "rb") as file:
    files = {"file": file}
    response = requests.post(url, headers=headers, files=files)
    print(response.json())
```

## Error Responses

### Common Error Codes

| Status Code | Description | Solution |
|-------------|-------------|----------|
| 400 | Bad Request - Invalid filename format | Check your filename follows the required pattern |
| 401 | Unauthorized - Invalid or missing token | Verify your Bearer token is correct |
| 409 | Conflict - File already exists | File with this name was already uploaded |
| 422 | Validation Error - No file provided | Ensure you're including the file in your request |

### Authentication Errors

**Missing Authorization Header:**
```json
{
  "detail": "Authorization header is required"
}
```
**Solution:** Add the Authorization header with your Bearer token.

**Invalid Bearer Token:**
```json
{
  "detail": "Invalid bearer token"
}
```
**Solution:** Verify your token is correct and active.

### File Validation Errors

**Invalid Filename Format:**
```json
{
  "detail": "Invalid filename format. Expected: PartnerID_CageID_YYYY-MM-DD_SampleID.fastq"
}
```
**Solution:** Rename your file to follow the exact naming convention.

**File Too Large:**
```json
{
  "detail": "File size exceeds maximum limit of 100MB"
}
```
**Solution:** Compress your file or contact support for large file handling.

## File Management

### Check Uploaded Files

You can view all your uploaded files:

```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  https://your-server-domain.com/api/v1/upload/files
```

**Response:**
```json
{
  "files": [
    {
      "filename": "Mowi_CAGE-04B_2025-08-15_S01.fastq",
      "partner_id": "Mowi",
      "cage_id": "CAGE-04B",
      "sample_date": "2025-08-15",
      "sample_id": "S01",
      "file_size": 1048576,
      "upload_time": 1692097200.0
    }
  ],
  "total_count": 1
}
```

## Best Practices

### File Preparation
- **Validate your files** before uploading to ensure they're properly formatted FASTQ files
- **Check file size** - files larger than 100MB may require special handling
- **Use consistent naming** - maintain the same PartnerID across all your uploads

### Upload Process
- **Upload during business hours** when technical support is available
- **Verify successful upload** by checking the response message
- **Keep upload confirmations** for your records

### Troubleshooting
- **Connection issues:** Verify the server URL and your internet connection
- **Authentication issues:** Confirm your Bearer token is active and correctly formatted
- **File issues:** Ensure your FASTQ files are not corrupted and follow naming conventions

## Support

If you encounter issues not covered in this guide:

1. **Check the error message** in the API response for specific guidance
2. **Verify your file format** and naming convention
3. **Test with a smaller file** if experiencing upload issues
4. **Contact technical support** with the specific error message you received

## Analysis Process

After successful upload:
1. Your files will be queued for bioinformatics analysis
2. The SRS risk assessment model will process your sequence data
3. Results will be available on the dashboard (separate access instructions provided)
4. Critical risk scores will trigger manual alerts from our analysis team

## Security Notes

- **Keep your Bearer token secure** - do not share it or include it in version control
- **Use HTTPS** for all API communications
- **Files are processed securely** according to data protection standards
- **Contact support immediately** if you suspect token compromise
