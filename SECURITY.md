# Amrita Security Configuration

## Security Features

### Authentication Security

- **Password Requirements**: 
  - Minimum 16 characters
  - Requires uppercase, lowercase, digits, and special characters
  - Automatically generated secure passwords
  - No hardcoded default credentials

- **Rate Limiting**:
  - Login: 10 attempts per second per IP
  - API: 100 requests per minute per IP
  - Automatic IP blocking after limit exceeded

### Web Application Security

- **Security Headers**:
  - Content Security Policy (CSP)
  - X-XSS-Protection
  - X-Content-Type-Options
  - X-Frame-Options
  - Referrer-Policy
  - Permissions-Policy

- **Session Management**:
  - Secure, HTTP-only cookies
  - Token expiration and rotation
  - One-time token support

### File System Security

- **File Access Controls**:
  - Only `.env*` files can be managed via API
  - Path traversal protection
  - Malicious content detection

- **Configuration Protection**:
  - Sensitive data masking in logs
  - Secure file handling
  - Input validation and sanitization

## Security Configuration

### Environment Variables

```env
# Security Settings
WEBUI_USER_NAME=admin
WEBUI_PASSWORD=your_secure_password_here

# Rate Limiting (optional)
RATE_LIMIT_LOGIN=10
RATE_LIMIT_API=100

# Security Headers (optional)
CSP_POLICY="default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'self'; form-action 'self'"
```

## Security Best Practices

### For Developers

1. **Input Validation**: Always validate and sanitize user input
2. **Error Handling**: Never expose sensitive information in error messages
3. **Logging**: Mask sensitive data in logs
4. **Dependencies**: Keep all dependencies up to date
5. **Code Reviews**: Include security considerations in code reviews

### For Administrators

1. **Credentials**: Always use strong, unique passwords
2. **Updates**: Keep the application and dependencies updated
3. **Backups**: Regularly backup configuration and data
4. **Monitoring**: Monitor for suspicious activity
5. **Access Control**: Restrict access to management interfaces

### For Users

1. **Passwords**: Change default passwords immediately
2. **Access**: Only access the application over secure networks
3. **Reporting**: Report any suspicious activity
4. **Updates**: Keep client applications updated

## Security Testing

### Automated Tests

```bash
# Run security linting
ruff check --select S .

# Check for common vulnerabilities
bandit -r .

# Dependency vulnerability scanning
uv pip list --outdated
```

### Manual Testing

1. **Authentication Testing**:
   - Test password strength requirements
   - Verify rate limiting works
   - Test session management

2. **File Access Testing**:
   - Verify only `.env*` files can be accessed
   - Test path traversal protection
   - Verify content validation

3. **API Testing**:
   - Test input validation
   - Verify rate limiting
   - Test error handling

## Incident Response

### Security Incident Reporting

If you discover a security vulnerability, please report it responsibly:

1. **Do not** create public GitHub issues for security vulnerabilities
2. Contact the security team privately
3. Provide detailed reproduction steps
4. Allow reasonable time for fixes before disclosure

### Security Patch Process

1. **Triage**: Assess severity and impact
2. **Fix**: Develop and test security patches
3. **Release**: Publish security updates
4. **Disclosure**: Responsible disclosure to users

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://docs.python.org/3/howto/security.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

## Security Contact

For security-related inquiries, please contact:

- **Security Team**: security@amrita-project.org
- **Emergency**: security-emergency@amrita-project.org

**Note**: This is a template security configuration. Actual security practices may vary based on deployment requirements and threat landscape.