# Docker Security Best Practices

## 🔒 Secure Environment Variables Setup

### **1. Environment Files Structure**

```
.env                    # Production secrets (NEVER commit)
.env.development       # Development defaults (Safe to commit)
.env.production        # Production template (Safe to commit)
.env.example          # Example template (Safe to commit)
```

### **2. Security Files Created**

| File | Purpose | Security Level |
|------|---------|----------------|
| `.env.production` | Production template | ✅ Safe to commit |
| `.env.development` | Development defaults | ✅ Safe to commit |
| `setup-security.sh` | Auto-secure setup | ✅ Safe to commit |
| `security_settings.py` | Django security config | ✅ Safe to commit |

### **3. Quick Secure Setup**

```bash
# 1. Generate secure .env file
chmod +x setup-security.sh
./setup-security.sh

# 2. Update sensitive values
nano .env  # Update email, domains, etc.

# 3. Deploy securely
docker-compose up --build -d
```

### **4. Security Features**

#### **🔐 Environment Security:**
- ✅ **Auto-generated secrets** (50+ characters)
- ✅ **Separate JWT secret** from Django secret
- ✅ **Environment-specific settings**
- ✅ **Secure defaults** for production

#### **🛡️ Django Security:**
- ✅ **SSL redirects** in production
- ✅ **HSTS headers** for HTTPS enforcement
- ✅ **Secure cookies** (HttpOnly, Secure, SameSite)
- ✅ **CSRF protection** with trusted origins
- ✅ **Content type protection**
- ✅ **XSS filtering**

#### **📧 Email Security:**
- ✅ **Gmail App Passwords** (not regular passwords)
- ✅ **Console backend** for development
- ✅ **TLS encryption** for SMTP

#### **📁 File Security:**
- ✅ **Upload size limits**
- ✅ **Secure file permissions**
- ✅ **Memory limits** for uploads

### **5. Production Security Checklist**

#### **🔑 Secrets Management:**
- [ ] Generate unique SECRET_KEY
- [ ] Generate unique JWT_SECRET_KEY
- [ ] Use Gmail App Passwords
- [ ] Never commit .env to Git
- [ ] Rotate secrets regularly

#### **🌐 Network Security:**
- [ ] Configure SSL certificates
- [ ] Set up firewall rules
- [ ] Use HTTPS only
- [ ] Configure CORS properly
- [ ] Set trusted origins

#### **🍪 Cookie Security:**
- [ ] Secure cookies enabled
- [ ] HttpOnly cookies
- [ ] SameSite Strict
- [ ] Short session lifetime

#### **📊 Monitoring:**
- [ ] Enable logging
- [ ] Set up error tracking
- [ ] Monitor failed logins
- [ ] Backup database regularly

### **6. Docker Security**

#### **Container Security:**
```yaml
# In docker-compose.yml
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp
user: "1000:1000"  # Non-root user
```

#### **Network Security:**
```yaml
# Isolate containers
networks:
  - frontend
  - backend
  - database
```

### **7. Environment Variables Reference**

#### **Required Variables:**
```bash
# Core Django
SECRET_KEY=your-50-char-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
SQLITE_DB_PATH=/app/data/db.sqlite3

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### **Optional Variables:**
```bash
# JWT
JWT_SECRET_KEY=different-from-django-secret
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=7

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO

# File Uploads
FILE_UPLOAD_MAX_MEMORY_SIZE=5242880
```

### **8. Git Security**

#### **.gitignore Configuration:**
```gitignore
# Environment files
.env
.env.local
.env.production.local

# Database
*.sqlite3
*.db

# Logs
logs/
*.log

# Media
media/
```

### **9. Deployment Security**

#### **Production Deployment:**
```bash
# 1. Secure setup
./setup-security.sh

# 2. Update values
nano .env

# 3. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify security
curl -I https://yourdomain.com
```

#### **Security Headers Check:**
```bash
# Check security headers
curl -I https://yourdomain.com
# Look for: Strict-Transport-Security, X-Content-Type-Options, etc.
```

### **10. Troubleshooting**

#### **Common Issues:**
- **SSL errors**: Check certificate configuration
- **Email failures**: Verify Gmail App Password
- **Cookie issues**: Ensure HTTPS in production
- **CORS errors**: Update trusted origins

#### **Security Testing:**
```bash
# Test security headers
nmap --script http-security-headers yourdomain.com

# Test SSL configuration
testssl.sh yourdomain.com

# Test for vulnerabilities
owasp-zap-baseline.py -t https://yourdomain.com
```

This setup provides enterprise-grade security for your Django application in Docker! 🛡️✨
