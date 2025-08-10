# API Endpoints

This page provides detailed information about all available API endpoints.

## Core Application

::: app.main
    options:
      show_source: true
      heading_level: 3
      show_bases: false
      show_inheritance_diagram: false

## Configuration

::: app.config
    options:
      show_source: true
      heading_level: 3
      members_order: source
      show_bases: false

## Health Check

The API provides health check endpoints for monitoring:

### GET /

Returns basic application information and health status.

**Response:**
```json
{
  "message": "Project Thalassa API",
  "version": "0.1.0",
  "status": "operational"
}
```

### GET /health

Detailed health check endpoint for monitoring systems.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "0.1.0",
  "environment": "development"
}
```

## File Upload Endpoints

### POST /api/v1/upload

Upload a fastq file for bioinformatics analysis. The file must follow the naming convention:
`PartnerID_CageID_YYYY-MM-DD_SampleID.fastq`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Parameters:
  - `file`: The fastq file to upload

**Example filename:** `Mowi_CAGE-04B_2025-08-15_S01.fastq`

**Response (200 - Success):**
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
    "file_size": 1024
  }
}
```

**Error Responses:**
- `400` - Invalid filename format or fastq content
- `409` - File with the same name already exists
- `422` - No file provided or validation error

### GET /api/v1/upload/files

List all uploaded fastq files with their metadata.

**Response (200 - Success):**
```json
{
  "files": [
    {
      "filename": "Mowi_CAGE-04B_2025-08-15_S01.fastq",
      "partner_id": "Mowi",
      "cage_id": "CAGE-04B",
      "sample_date": "2025-08-15",
      "sample_id": "S01",
      "file_size": 1024,
      "upload_time": 1704067800.0
    }
  ],
  "total_count": 1
}
```

### GET /api/v1/upload/health

Health check endpoint for upload service.

**Response (200 - Success):**
```json
{
  "status": "healthy",
  "service": "upload",
  "upload_directory": "/uploads",
  "directory_exists": true
}
```

## API Modules

Planned API endpoints for future development:

- **Authentication** - Bearer token authentication (Issue #25)
- **Analysis** - Risk assessment and processing endpoints
- **Results** - Query and retrieve analysis results
- **Dashboard** - Aggregate data for dashboard views

## Error Responses

All endpoints may return these error responses:

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error occurred"
}
```
