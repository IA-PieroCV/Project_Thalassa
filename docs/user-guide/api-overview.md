# API Overview

Project Thalassa provides a RESTful API for bioinformatics data analysis and SRS risk assessment.

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Authentication

All data endpoints require Bearer token authentication:

```http
Authorization: Bearer YOUR_TOKEN_HERE
```

Obtain your token from your system administrator or partner coordinator.

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/` | GET | Application info | No |
| `/health` | GET | Health check | No |
| `/docs` | GET | Interactive API documentation | No |
| `/redoc` | GET | Alternative API documentation | No |

### Upload Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/v1/upload` | POST | Upload FASTQ file | Yes |
| `/api/v1/upload/files` | GET | List uploaded files | Yes |
| `/api/v1/upload/health` | GET | Upload service health | No |

### Dashboard Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/v1/dashboard` | GET | View risk assessment dashboard (shows all analyses) | Yes |
| `/api/v1/dashboard/data` | GET | Get risk assessment data in JSON format | Yes |
| `/api/v1/dashboard/health` | GET | Dashboard service health | No |

## Request/Response Format

### Request Headers

```http
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN_HERE
Accept: application/json
```

### Standard Response Format

Success Response (200 OK):
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation successful"
}
```

Error Response (4xx/5xx):
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

## File Upload API

### Upload FASTQ File

**Endpoint:** `POST /api/v1/upload`

**Request:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/file.fastq" \
  http://localhost:8000/api/v1/upload
```

**Response (200 OK):**
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
    "file_size": 2428613,
    "upload_time": "2025-08-11T12:00:00Z"
  }
}
```

### List Uploaded Files

**Endpoint:** `GET /api/v1/upload/files`

**Request:**
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/upload/files
```

**Response (200 OK):**
```json
{
  "files": [
    {
      "filename": "Mowi_CAGE-04B_2025-08-15_S01.fastq",
      "size": 2428613,
      "uploaded_at": "2025-08-11T12:00:00Z",
      "metadata": {
        "partner_id": "Mowi",
        "cage_id": "CAGE-04B",
        "sample_date": "2025-08-15"
      }
    }
  ],
  "total": 1
}
```

## Dashboard API

### View Risk Assessment Dashboard

**Endpoint:** `GET /api/v1/dashboard`

**Request:**
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept: text/html" \
  http://localhost:8000/api/v1/dashboard
```

**Response:** HTML page with risk assessment visualization

The dashboard automatically detects whether you have single or multiple analysis results:
- **Multiple Results**: Shows batch analysis summary, risk distribution, and detailed table view
- **Single Result**: Shows traditional single-entry view with metadata details

### Get Risk Data (JSON)

**Endpoint:** `GET /api/v1/dashboard/data`

**Request:**
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/dashboard/data
```

**Response for Multiple Results (200 OK):**
```json
[
  {
    "cageId": "CAGE-04A",
    "srsRiskScore": 0.752,
    "riskLevel": "HIGH",
    "lastUpdated": "2025-08-16T10:30:00Z"
  },
  {
    "cageId": "CAGE-04B",
    "srsRiskScore": 0.423,
    "riskLevel": "MEDIUM",
    "lastUpdated": "2025-08-16T11:15:00Z"
  },
  {
    "cageId": "CAGE-05A",
    "srsRiskScore": 0.189,
    "riskLevel": "LOW",
    "lastUpdated": "2025-08-16T11:45:00Z"
  }
]
```

**Response for Single Result (200 OK):**
```json
{
  "risk_assessments": [
    {
      "cageId": "CAGE-04B",
      "srsRiskScore": 0.65,
      "riskLevel": "HIGH",
      "lastUpdated": "2025-08-11T12:00:00Z",
      "details": {
        "samples_analyzed": 1,
        "confidence": 0.95
      }
    }
  ],
  "summary": {
    "total_cages": 1,
    "critical_risk": 0,
    "high_risk": 1,
    "medium_risk": 0,
    "low_risk": 0
  }
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_REQUIRED` | 401 | Authentication token missing |
| `AUTH_INVALID` | 401 | Invalid authentication token |
| `AUTH_EXPIRED` | 401 | Authentication token expired |
| `FILE_TOO_LARGE` | 413 | File exceeds maximum size |
| `INVALID_FORMAT` | 400 | Invalid file format or naming |
| `NOT_FOUND` | 404 | Resource not found |
| `SERVER_ERROR` | 500 | Internal server error |

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Default limit:** 60 requests per minute per IP
- **Upload endpoint:** 10 requests per minute per token
- **Dashboard endpoint:** 30 requests per minute per token

Rate limit headers:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1628789100
```

## API Versioning

The API uses URL versioning:

- Current version: `v1`
- Base path: `/api/v1/`

Example:
```
http://localhost:8000/api/v1/upload
```

## SDK Support

### Python Client

```python
import requests

class ThalassaClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def upload_file(self, filepath):
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/api/v1/upload",
                headers=self.headers,
                files=files
            )
        return response.json()

    def get_dashboard_data(self):
        response = requests.get(
            f"{self.base_url}/api/v1/dashboard/data",
            headers=self.headers
        )
        return response.json()

# Usage
client = ThalassaClient("http://localhost:8000", "YOUR_TOKEN")
result = client.upload_file("sample.fastq")
print(result)
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class ThalassaClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = { 'Authorization': `Bearer ${token}` };
    }

    async uploadFile(filepath) {
        const form = new FormData();
        form.append('file', fs.createReadStream(filepath));

        const response = await axios.post(
            `${this.baseUrl}/api/v1/upload`,
            form,
            { headers: { ...this.headers, ...form.getHeaders() } }
        );
        return response.data;
    }

    async getDashboardData() {
        const response = await axios.get(
            `${this.baseUrl}/api/v1/dashboard/data`,
            { headers: this.headers }
        );
        return response.data;
    }
}

// Usage
const client = new ThalassaClient('http://localhost:8000', 'YOUR_TOKEN');
client.uploadFile('sample.fastq')
    .then(result => console.log(result))
    .catch(error => console.error(error));
```

## Testing the API

### Using cURL

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test authenticated upload
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.fastq" \
  http://localhost:8000/api/v1/upload
```

### Using Postman

1. Import the API collection from `/docs/postman_collection.json`
2. Set your Bearer token in the collection variables
3. Run the requests in the collection

### Using the Interactive Docs

Visit `http://localhost:8000/docs` for interactive API testing with Swagger UI.

## Best Practices

1. **Always use HTTPS in production** to protect authentication tokens
2. **Store tokens securely** and never commit them to version control
3. **Handle rate limits gracefully** with exponential backoff
4. **Validate file formats** before uploading
5. **Monitor API usage** through the dashboard metrics
6. **Cache responses** when appropriate to reduce server load

## Support

For API support and questions:
- Review the [FAQ](/faq)
- Check [GitHub Issues](https://github.com/IA-PieroCV/Project_Thalassa/issues)
- Contact technical support at support@thalassa.example.com
