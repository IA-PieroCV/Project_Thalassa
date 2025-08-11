# User Acceptance Testing (UAT) Guide

This guide provides step-by-step procedures for testing Project Thalassa before the v1.0.0 release.

## Test Environment Setup

### Prerequisites

- Docker and Docker Compose installed
- Test FASTQ files available
- Valid Bearer token for authentication
- Web browser for dashboard testing

### Starting the Test Environment

```bash
# Clone the repository
git clone https://github.com/IA-PieroCV/Project_Thalassa.git
cd Project_Thalassa

# Copy and configure environment
cp .env.example .env
# Edit .env and set appropriate values

# Start services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check application health
curl http://localhost:8000/health
```

## UAT Test Scenarios

### Test Scenario 1: Health Check

**Objective:** Verify the system is operational

**Steps:**
1. Open browser to http://localhost:8000
2. Verify welcome message appears
3. Navigate to http://localhost:8000/health
4. Verify health status shows "healthy"

**Expected Result:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-11T12:00:00Z",
  "version": "1.0.0",
  "environment": "development"
}
```

**Pass Criteria:** ✅ Health endpoint returns 200 OK with valid JSON

---

### Test Scenario 2: File Upload Authentication

**Objective:** Verify authentication is required for uploads

**Steps:**
1. Attempt upload without authentication:
```bash
curl -X POST \
  -F "file=@test.fastq" \
  http://localhost:8000/api/v1/upload
```

2. Verify 401 Unauthorized response
3. Attempt with invalid token:
```bash
curl -X POST \
  -H "Authorization: Bearer invalid-token" \
  -F "file=@test.fastq" \
  http://localhost:8000/api/v1/upload
```

4. Verify 401 response with error message

**Expected Result:** Authentication errors for both attempts

**Pass Criteria:** ✅ Unauthorized requests are rejected

---

### Test Scenario 3: Valid File Upload

**Objective:** Successfully upload a properly formatted FASTQ file

**Test Data:** Create test file `Mowi_CAGE-04B_2025-08-15_S01.fastq`:
```
@SEQ_ID_001
GATCGATCGATCGATCGATCGATC
+
IIIIIIIIIIIIIIIIIIIIIIII
@SEQ_ID_002
ATCGATCGATCGATCGATCGATCG
+
HHHHHHHHHHHHHHHHHHHHHHHH
```

**Steps:**
1. Upload file with valid authentication:
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@Mowi_CAGE-04B_2025-08-15_S01.fastq" \
  http://localhost:8000/api/v1/upload
```

2. Verify successful response
3. Check file appears in uploads directory:
```bash
ls -la uploads/
```

**Expected Result:**
```json
{
  "message": "File uploaded successfully",
  "filename": "Mowi_CAGE-04B_2025-08-15_S01.fastq",
  "metadata": {
    "partner_id": "Mowi",
    "cage_id": "CAGE-04B",
    "sample_date": "2025-08-15",
    "sample_id": "S01"
  }
}
```

**Pass Criteria:** ✅ File uploads successfully with correct metadata extraction

---

### Test Scenario 4: Invalid Filename Format

**Objective:** Verify system rejects improperly named files

**Test Files:**
- `invalid_filename.fastq`
- `Mowi-CAGE-04B-2025-08-15-S01.fastq` (wrong separator)
- `Mowi_CAGE-04B_15-08-2025_S01.fastq` (wrong date format)

**Steps:**
1. Attempt to upload each invalid file
2. Verify each returns 400 Bad Request
3. Check error message explains the issue

**Expected Result:** Clear error messages for each invalid format

**Pass Criteria:** ✅ Invalid filenames are rejected with helpful errors

---

### Test Scenario 5: Dashboard Access

**Objective:** Verify dashboard displays risk assessment data

**Steps:**
1. Access dashboard with authentication:
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept: text/html" \
  http://localhost:8000/api/v1/dashboard
```

2. Open in browser (with auth header tool)
3. Verify dashboard loads
4. Check for risk score display
5. Verify cage information is shown

**Expected Result:** Dashboard displays with risk assessment visualization

**Pass Criteria:** ✅ Dashboard renders correctly with data

---

### Test Scenario 6: Batch Analysis

**Objective:** Test the batch analysis functionality

**Steps:**
1. Place multiple FASTQ files in uploads directory
2. Run batch analysis:
```bash
docker exec thalassa-app python scripts/generate_results.py
```

3. Check results.json is generated:
```bash
cat results/results.json
```

4. Verify dashboard reflects new results

**Expected Result:** Results file generated with risk scores

**Pass Criteria:** ✅ Batch analysis completes and generates results

---

### Test Scenario 7: File Size Limits

**Objective:** Verify file size restrictions work

**Steps:**
1. Create large test file (>100MB):
```bash
dd if=/dev/zero of=large_file.fastq bs=1M count=101
```

2. Attempt upload
3. Verify rejection with 413 error

**Expected Result:** File too large error

**Pass Criteria:** ✅ Large files are rejected appropriately

---

### Test Scenario 8: Concurrent Uploads

**Objective:** Test system handles multiple simultaneous uploads

**Steps:**
1. Prepare 5 valid FASTQ files with different names
2. Upload simultaneously using parallel:
```bash
ls *.fastq | parallel -j 5 \
  'curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
   -F "file=@{}" http://localhost:8000/api/v1/upload'
```

3. Verify all uploads succeed
4. Check all files in uploads directory

**Expected Result:** All files upload successfully

**Pass Criteria:** ✅ System handles concurrent uploads

---

### Test Scenario 9: API Documentation

**Objective:** Verify API documentation is accessible

**Steps:**
1. Navigate to http://localhost:8000/docs
2. Verify Swagger UI loads
3. Test "Try it out" for health endpoint
4. Navigate to http://localhost:8000/redoc
5. Verify ReDoc documentation loads

**Expected Result:** Both documentation interfaces work

**Pass Criteria:** ✅ API documentation is complete and functional

---

### Test Scenario 10: Error Recovery

**Objective:** Test system recovery from errors

**Steps:**
1. Stop the application:
```bash
docker-compose stop app
```

2. Attempt to access endpoints (should fail)
3. Restart application:
```bash
docker-compose start app
```

4. Wait for health check to pass
5. Verify normal operations resume

**Expected Result:** System recovers gracefully

**Pass Criteria:** ✅ Application restarts and resumes normal operation

## Performance Testing

### Load Test

Test system under load:

```bash
# Install Apache Bench if not available
apt-get install apache2-utils

# Test health endpoint performance
ab -n 1000 -c 10 http://localhost:8000/health

# Test with authentication (create post_data file first)
ab -n 100 -c 5 -T 'multipart/form-data' \
   -H "Authorization: Bearer YOUR_TOKEN" \
   -p post_data http://localhost:8000/api/v1/upload
```

**Acceptance Criteria:**
- Health endpoint: >100 requests/second
- Upload endpoint: >10 requests/second
- No errors under normal load

## Security Testing

### Test Checklist

- [ ] Authentication required for all data endpoints
- [ ] Invalid tokens are rejected
- [ ] No sensitive data in responses
- [ ] CORS headers properly configured
- [ ] No directory traversal vulnerabilities
- [ ] SQL injection not possible (if DB used)
- [ ] File upload validates extensions
- [ ] Rate limiting works (if configured)

## UAT Sign-off Checklist

### Functional Requirements

- [ ] File upload works with proper authentication
- [ ] Filename validation enforces naming convention
- [ ] Metadata correctly extracted from filenames
- [ ] Dashboard displays risk assessment data
- [ ] Batch analysis generates results.json
- [ ] API documentation is accessible
- [ ] Health checks pass

### Non-Functional Requirements

- [ ] Response times acceptable (<2s for uploads)
- [ ] System handles concurrent users
- [ ] Error messages are helpful
- [ ] Logs capture important events
- [ ] Docker deployment works smoothly
- [ ] Documentation is complete

### Partner-Specific Tests

- [ ] Partner can authenticate successfully
- [ ] Partner can upload their FASTQ files
- [ ] Partner can view risk assessments
- [ ] Partner receives appropriate error messages
- [ ] Partner API guide is accurate

## Issue Reporting

If you encounter issues during UAT:

1. **Document the Issue:**
   - Test scenario number
   - Steps to reproduce
   - Expected vs actual result
   - Screenshots if applicable
   - Log excerpts

2. **Check Logs:**
```bash
# Application logs
docker-compose logs app

# Follow logs in real-time
docker-compose logs -f app
```

3. **Report Format:**
```markdown
**Issue:** [Brief description]
**Scenario:** Test Scenario X
**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
**Expected:** [What should happen]
**Actual:** [What actually happened]
**Logs:** [Relevant log entries]
```

## UAT Completion

Once all test scenarios pass:

1. **Generate Test Report**
2. **Document any issues found**
3. **Verify fixes for any issues**
4. **Obtain sign-off from stakeholders**
5. **Proceed to production release**

## Rollback Plan

If critical issues are found:

1. Stop docker containers: `docker-compose down`
2. Revert to previous version: `git checkout <previous-tag>`
3. Rebuild and restart: `docker-compose up --build -d`
4. Verify rollback successful
5. Document issues for resolution
