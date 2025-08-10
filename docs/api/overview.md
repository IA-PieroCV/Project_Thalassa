# API Reference

Project Thalassa provides a REST API built with FastAPI for all platform interactions.

## Interactive Documentation

The API includes automatically generated interactive documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) - Interactive API explorer
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc) - Alternative documentation view
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) - Machine-readable API specification

## Base URL

When running locally:
```
http://localhost:8000
```

## Authentication

!!! note "Development Mode"
    Authentication is currently under development. The API accepts requests without authentication in development mode.

## API Modules

The API is organized into logical modules:

::: app.main
    options:
      show_source: false
      heading_level: 3

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... }
  }
}
```

## Status Codes

The API uses standard HTTP status codes:

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Rate Limiting

!!! info "Future Feature"
    Rate limiting will be implemented in future versions to ensure fair usage.

## SDK Generation

The OpenAPI specification can be used to generate client SDKs in multiple languages:

```bash
# Generate Python client
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o ./client-python

# Generate JavaScript client
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g javascript -o ./client-js
```

## WebSocket Support

!!! info "Future Feature"
    Real-time updates via WebSocket will be available in future versions for monitoring analysis progress.

---

For detailed endpoint documentation, see [Endpoints](endpoints.md).
