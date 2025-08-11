# Bearer Token Security Guide - Project Thalassa

**CONFIDENTIAL - INTERNAL USE ONLY**

This document contains sensitive security information for managing Bearer Token authentication in Project Thalassa. Do not share this document with external parties.

## Overview

Project Thalassa uses Bearer Token authentication to secure access to:
- File upload API endpoints (`/api/v1/upload`)
- Dashboard web interface (`/`)
- Administrative endpoints

This guide provides internal procedures for Bearer Token generation, management, and secure partner communication.

## Token Architecture

### Authentication Flow
1. Partner includes Bearer Token in `Authorization: Bearer <token>` header
2. FastAPI `HTTPBearer` security extracts token from request
3. `AuthService.validate_bearer_token()` validates against configured token
4. Request proceeds if valid, returns 401 if invalid

### Security Implementation
- **Simple constant-time comparison** prevents timing attacks
- **Configurable via environment variables** for security flexibility
- **WWW-Authenticate headers** provide proper HTTP authentication flow
- **Comprehensive logging** for security monitoring

## Bearer Token Management

### Token Generation

#### Recommended Token Generation Methods

**Option 1: OpenSSL (Recommended)**
```bash
# Generate 256-bit (32 bytes) random token, base64 encoded
openssl rand -base64 32
```

**Option 2: Python (Alternative)**
```python
import secrets
import base64

# Generate 256-bit secure random token
token_bytes = secrets.token_bytes(32)
bearer_token = base64.urlsafe_b64encode(token_bytes).decode('utf-8').rstrip('=')
print(f"BEARER_TOKEN={bearer_token}")
```

**Option 3: UUID4 (Simple Alternative)**
```bash
# Generate UUID4-based token (128-bit entropy)
python -c "import uuid; print('BEARER_TOKEN=' + str(uuid.uuid4()).replace('-', ''))"
```

### Token Storage

#### Production Environment
1. **Environment Variable**: Set `BEARER_TOKEN` in production environment
2. **Secrets Management**: Use secure secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
3. **Never Store in Code**: Tokens must never be committed to version control

#### Development Environment
1. Copy `.env.example` to `.env`
2. Generate new token using methods above
3. Replace `BEARER_TOKEN="your-bearer-token-here-change-in-production"`
4. Ensure `.env` is in `.gitignore` (already configured)

### Token Security Requirements

#### Token Characteristics
- **Minimum Length**: 32 characters
- **Entropy**: At least 256 bits of randomness
- **Character Set**: Base64 or hexadecimal encoding preferred
- **Uniqueness**: Each environment must use different tokens

#### Security Standards
- **Development Tokens**: Generate new token for each developer environment
- **Production Tokens**: Generate separate tokens for each partner/deployment
- **No Reuse**: Never reuse tokens between environments or partners

## Partner Communication Protocol

### Initial Token Delivery

#### Step 1: Generate Partner-Specific Token
```bash
# Generate unique token for the partner
PARTNER_TOKEN=$(openssl rand -base64 32)
echo "Generated token for [Partner Name]: $PARTNER_TOKEN"
```

#### Step 2: Secure Communication Channels

**Primary Method: Encrypted Email + Phone Verification**
1. Send encrypted email with token to partner's designated security contact
2. Use partner's PGP public key if available
3. Follow up with phone call to confirm receipt
4. Request written confirmation of token receipt

**Alternative Method: Secure Portal**
1. Use partner's existing secure document portal if available
2. Upload token document with password protection
3. Communicate password through separate secure channel

**Emergency Method: In-Person/Video Call**
1. Schedule secure video conference with partner technical lead
2. Share token verbally during call
3. Request immediate confirmation and secure storage

#### Step 3: Delivery Documentation Template

```
Subject: [SECURE] Project Thalassa API Authentication Token

Dear [Partner Security Contact],

This message contains sensitive authentication credentials for Project Thalassa's bioinformatics analysis platform.

AUTHENTICATION TOKEN:
[INSERT_TOKEN_HERE]

SECURITY REQUIREMENTS:
- Store this token securely (encrypted storage recommended)
- Do not share outside your authorized technical team
- Include in Authorization header: "Authorization: Bearer [TOKEN]"
- Token is case-sensitive and must be used exactly as provided

ENDPOINTS REQUIRING AUTHENTICATION:
- API Upload: https://[DOMAIN]/api/v1/upload
- Dashboard: https://[DOMAIN]/

Please confirm receipt of this token within 24 hours by replying to this email.

For technical support or token-related issues, contact:
- Email: [TECHNICAL_CONTACT_EMAIL]
- Phone: [TECHNICAL_CONTACT_PHONE]

This token will be active immediately upon confirmation of receipt.

Best regards,
[YOUR_NAME]
Project Thalassa Security Team
```

### Partner Integration Testing

#### Pre-Production Verification
1. **Test Token**: Provide test token for integration testing
2. **Sandbox Environment**: Use separate test environment if available
3. **Verification Calls**: Test authentication endpoints before production

#### Integration Checklist
```
□ Partner confirms token storage in secure location
□ Partner technical team tests file upload authentication
□ Partner technical team tests dashboard access
□ Partner understands error handling for invalid tokens
□ Partner has backup contact for token-related issues
□ Partner confirms understanding of token rotation process
```

## Token Rotation and Lifecycle Management

### Scheduled Rotation

#### Rotation Frequency
- **Production**: Every 90 days (recommended)
- **High-Security Partners**: Every 30 days
- **Emergency**: Immediate rotation if compromise suspected

#### Rotation Process
1. **Generate New Token**: Create replacement token using secure methods
2. **Coordinate with Partner**: Schedule rotation window (minimum 48-hour notice)
3. **Deploy New Token**: Update production environment variables
4. **Notify Partner**: Provide new token using secure communication
5. **Verify New Token**: Confirm partner integration works
6. **Revoke Old Token**: Remove old token after confirmation period (24 hours)

### Emergency Revocation

#### Immediate Actions
1. **Revoke Current Token**: Set `BEARER_TOKEN=""` in production environment
2. **Monitor Access Logs**: Review authentication attempts
3. **Generate New Token**: Create replacement immediately
4. **Emergency Contact**: Notify partner via phone within 1 hour
5. **Document Incident**: Record revocation reason and timeline

### Token Monitoring

#### Security Monitoring
- **Failed Authentication Attempts**: Monitor 401 responses for suspicious activity
- **Geographic Anomalies**: Alert on access from unexpected locations
- **Usage Patterns**: Track normal vs. abnormal API usage
- **Log Analysis**: Regular review of authentication logs

#### Monitoring Queries
```bash
# Check failed authentication attempts
grep "Authentication failed" /var/log/thalassa.log | tail -20

# Monitor bearer token usage patterns
grep "Authorization.*Bearer" /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -nr
```

## Troubleshooting Guide

### Common Authentication Issues

#### 401 Unauthorized - "Authorization header is required"
**Cause**: Missing Authorization header
**Solution**: Partner must include header: `Authorization: Bearer <token>`

#### 401 Unauthorized - "Invalid bearer token"
**Cause**: Token mismatch or expired
**Solutions**:
1. Verify token matches exactly (no extra spaces/characters)
2. Check if token has been rotated
3. Confirm environment is pointing to correct token

#### 401 Unauthorized - "Invalid authorization header format"
**Cause**: Incorrect header format
**Solution**: Must use exact format: `Authorization: Bearer <token>`

### Partner Support Procedures

#### Token Verification Process
1. **Confirm Token Format**: Verify partner is using correct header format
2. **Test Token**: Use curl to test authentication:
```bash
curl -H "Authorization: Bearer [TOKEN]" https://[DOMAIN]/api/v1/upload/health
```
3. **Check Logs**: Review server logs for authentication attempts
4. **Generate Test Token**: Provide temporary token for testing if needed

#### Escalation Procedures
- **Level 1**: Technical support reviews authentication logs
- **Level 2**: Security team reviews token configuration
- **Level 3**: Emergency token rotation and partner coordination

## Security Incident Response

### Suspected Token Compromise

#### Immediate Actions (Within 15 minutes)
1. **Revoke Token**: Disable current token in production
2. **Assess Impact**: Review access logs for unauthorized activity
3. **Generate New Token**: Create secure replacement
4. **Alert Partner**: Emergency contact to security team

#### Investigation Process
1. **Log Analysis**: Full review of authentication and access logs
2. **Impact Assessment**: Determine scope of potential compromise
3. **Partner Coordination**: Work with partner security team
4. **Documentation**: Complete incident report

### Security Contact Information

#### Internal Contacts
- **Primary Security Contact**: [NAME] - [EMAIL] - [PHONE]
- **Technical Lead**: [NAME] - [EMAIL] - [PHONE]
- **Emergency Contact**: [NAME] - [EMAIL] - [PHONE]

#### Partner Emergency Contacts
- **Partner Security Team**: [PARTNER_EMAIL] - [PARTNER_PHONE]
- **Partner Technical Lead**: [PARTNER_EMAIL] - [PARTNER_PHONE]

## Compliance and Audit Trail

### Documentation Requirements
- **Token Generation**: Record date, method, and authorized personnel
- **Partner Delivery**: Document delivery method and confirmation
- **Rotation Events**: Log all token rotations with timestamps
- **Access Patterns**: Monitor and document normal usage patterns

### Audit Checklist
```
□ All tokens generated using approved methods
□ Partner delivery follows secure communication protocol
□ Rotation schedule maintained per policy
□ Security monitoring active and reviewed regularly
□ Incident response procedures tested quarterly
□ Documentation current and complete
```

---

**Document Classification**: CONFIDENTIAL
**Last Updated**: August 2025
**Version**: 1.0
**Owner**: Project Thalassa Security Team
