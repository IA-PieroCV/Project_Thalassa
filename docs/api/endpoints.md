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

## API Modules

As the application grows, API endpoints will be organized into modules:

- **Authentication** - User login, token management
- **File Upload** - Genomic data upload endpoints
- **Analysis** - Risk assessment and processing endpoints
- **Results** - Query and retrieve analysis results
- **Dashboard** - Aggregate data for dashboard views

!!! info "Under Development"
    Additional API endpoints are being developed. This documentation will be updated as new endpoints become available.

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
