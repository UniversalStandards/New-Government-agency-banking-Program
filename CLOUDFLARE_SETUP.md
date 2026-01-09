# Cloudflare Configuration for GOFAP

## Automated Cloudflare Setup Script

```bash
#!/bin/bash

# Cloudflare Configuration Script
# This script automates DNS, SSL, and security configuration

CLOUDFLARE_API_TOKEN="your_api_token_here"
CLOUDFLARE_ZONE_ID="your_zone_id_here"
CLOUDFLARE_EMAIL="your_email@domain.com"
AZURE_WEBAPP_URL="gofap-app.azurewebsites.net"
DOMAIN="gofap.gov"

# Function to make Cloudflare API calls
cf_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    curl -X $method "https://api.cloudflare.com/client/v4/$endpoint" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json" \
        --data "$data"
}

# 1. Create DNS Records
echo "Creating DNS records..."

# Root domain
cf_api POST "zones/$CLOUDFLARE_ZONE_ID/dns_records" '{
  "type": "CNAME",
  "name": "@",
  "content": "'$AZURE_WEBAPP_URL'",
  "ttl": 1,
  "proxied": true
}'

# www subdomain
cf_api POST "zones/$CLOUDFLARE_ZONE_ID/dns_records" '{
  "type": "CNAME",
  "name": "www",
  "content": "'$AZURE_WEBAPP_URL'",
  "ttl": 1,
  "proxied": true
}'

# 2. Configure SSL/TLS Settings
echo "Configuring SSL/TLS..."

cf_api PATCH "zones/$CLOUDFLARE_ZONE_ID/settings/ssl" '{
  "value": "full_strict"
}'

cf_api PATCH "zones/$CLOUDFLARE_ZONE_ID/settings/always_use_https" '{
  "value": "on"
}'

cf_api PATCH "zones/$CLOUDFLARE_ZONE_ID/settings/automatic_https_rewrites" '{
  "value": "on"
}'

cf_api PATCH "zones/$CLOUDFLARE_ZONE_ID/settings/min_tls_version" '{
  "value": "1.2"
}'

# 3. Configure Page Rules for Static Assets
echo "Creating page rules..."

cf_api POST "zones/$CLOUDFLARE_ZONE_ID/pagerules" '{
  "targets": [{
    "target": "url",
    "constraint": {
      "operator": "matches",
      "value": "*'$DOMAIN'/static/*"
    }
  }],
  "actions": [
    {"id": "cache_level", "value": "cache_everything"},
    {"id": "edge_cache_ttl", "value": 2592000},
    {"id": "browser_cache_ttl", "value": 86400}
  ],
  "priority": 1,
  "status": "active"
}'

# 4. Configure Security Settings
echo "Configuring security..."

# Enable Bot Fight Mode
cf_api PATCH "zones/$CLOUDFLARE_ZONE_ID/settings/bot_fight_mode" '{
  "value": "on"
}'

# Enable Browser Integrity Check
cf_api PATCH "zones/$CLOUDFLARE_ZONE_ID/settings/browser_check" '{
  "value": "on"
}'

# Configure Security Level
cf_api PATCH "zones/$CLOUDFLARE_ZONE_ID/settings/security_level" '{
  "value": "high"
}'

# 5. Enable Performance Features
echo "Enabling performance features..."

# Enable Brotli compression
cf_api PATCH "zones/$CLOUDFLARE_ZONE_ID/settings/brotli" '{
  "value": "on"
}'

# Enable Early Hints
cf_api PATCH "zones/$CLOUDFLARE_ZONE_ID/settings/early_hints" '{
  "value": "on"
}'

# Enable HTTP/2
cf_api PATCH "zones/$CLOUDFLARE_ZONE_ID/settings/http2" '{
  "value": "on"
}'

# Enable HTTP/3
cf_api PATCH "zones/$CLOUDFLARE_ZONE_ID/settings/http3" '{
  "value": "on"
}'

echo "Cloudflare configuration complete!"
```

## Manual Configuration Steps

### 1. DNS Configuration

**Root Domain (@)**
```
Type: CNAME
Name: @
Content: gofap-app.azurewebsites.net
TTL: Auto
Proxy status: Proxied (orange cloud)
```

**WWW Subdomain**
```
Type: CNAME
Name: www
Content: gofap-app.azurewebsites.net
TTL: Auto
Proxy status: Proxied (orange cloud)
```

**API Subdomain (optional)**
```
Type: CNAME
Name: api
Content: gofap-app.azurewebsites.net
TTL: Auto
Proxy status: Proxied (orange cloud)
```

### 2. SSL/TLS Configuration

Go to **SSL/TLS** → **Overview**:
- Encryption mode: **Full (strict)**
- ✅ Always Use HTTPS
- ✅ Automatic HTTPS Rewrites
- ✅ Opportunistic Encryption
- Minimum TLS Version: **TLS 1.2**

Go to **SSL/TLS** → **Edge Certificates**:
- ✅ Always Use HTTPS
- ✅ TLS 1.3
- ✅ Automatic HTTPS Rewrites
- ✅ Certificate Transparency Monitoring

### 3. Page Rules

**Rule 1: Cache Static Assets**
```
URL: *gofap.gov/static/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 4 hours
```

**Rule 2: Bypass Cache for API**
```
URL: *gofap.gov/api/*
Settings:
  - Cache Level: Bypass
  - Security Level: High
```

**Rule 3: Force HTTPS**
```
URL: http://gofap.gov/*
Settings:
  - Always Use HTTPS: On
```

**Rule 4: Admin Security**
```
URL: *gofap.gov/admin/*
Settings:
  - Cache Level: Bypass
  - Security Level: High
  - Browser Integrity Check: On
  - Email Obfuscation: On
```

### 4. Firewall Rules

**Rule 1: Block Known Threats**
```
Expression: (cf.threat_score gt 14)
Action: Challenge
Description: Challenge users with high threat scores
```

**Rule 2: Rate Limit Login**
```
Expression: (http.request.uri.path eq "/auth/login" and rate_limit())
Action: Block
Description: Block excessive login attempts
```

**Rule 3: Protect Admin Panel**
```
Expression: (http.request.uri.path contains "/admin" and not ip.geoip.country in {"US"})
Action: Challenge
Description: Extra security for admin panel from non-US IPs
```

**Rule 4: Block Suspicious Patterns**
```
Expression: (http.request.uri.query contains "script" or http.request.uri.query contains "select")
Action: Block
Description: Block potential SQL injection and XSS attempts
```

### 5. Speed Optimization

Go to **Speed** → **Optimization**:

**Content Optimization**
- ✅ Auto Minify: JavaScript, CSS, HTML
- ✅ Brotli compression
- ✅ Early Hints
- ⚠️ Rocket Loader (test before enabling)

**Protocol Optimization**
- ✅ HTTP/2
- ✅ HTTP/3 (with QUIC)
- ✅ 0-RTT Connection Resumption

**Image Optimization**
- ✅ Polish (Lossless)
- ✅ WebP conversion
- ✅ Mirage (mobile optimization)

### 6. Security Settings

Go to **Security** → **Settings**:
- Security Level: **High**
- ✅ Browser Integrity Check
- ✅ Privacy Pass Support
- ✅ Email Address Obfuscation
- ✅ Server-side Excludes
- ✅ Hotlink Protection

Go to **Security** → **WAF**:
- ✅ Managed Rules (OWASP Core Ruleset)
- ✅ Rate Limiting Rules
- Custom Rules: As defined above

### 7. Caching Configuration

Go to **Caching** → **Configuration**:

**Caching Level**: Standard

**Browser Cache TTL**: Respect Existing Headers

**Always Online**: ✅ Enabled

**Development Mode**: ❌ Disabled (enable only during testing)

### 8. Workers (Optional Advanced Setup)

Create a Cloudflare Worker for advanced routing:

```javascript
// GOFAP Cloudflare Worker
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  
  // Add security headers
  const headers = new Headers()
  headers.set('X-Frame-Options', 'DENY')
  headers.set('X-Content-Type-Options', 'nosniff')
  headers.set('X-XSS-Protection', '1; mode=block')
  headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  headers.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
  
  // Route to Azure backend
  const backendUrl = new URL(request.url)
  backendUrl.hostname = 'gofap-app.azurewebsites.net'
  
  const modifiedRequest = new Request(backendUrl, {
    method: request.method,
    headers: request.headers,
    body: request.body
  })
  
  let response = await fetch(modifiedRequest)
  
  // Clone response and add headers
  response = new Response(response.body, response)
  
  for (const [key, value] of headers.entries()) {
    response.headers.set(key, value)
  }
  
  return response
}
```

### 9. Analytics Configuration

Go to **Analytics** → **Web Analytics**:
- ✅ Enable Web Analytics
- ✅ Automatic setup
- Add Analytics beacon to site

### 10. Custom Domain Verification

After DNS propagation (24-48 hours):

1. Verify DNS records are active:
   ```bash
   dig gofap.gov
   nslookup gofap.gov
   ```

2. Test SSL certificate:
   ```bash
   openssl s_client -connect gofap.gov:443 -servername gofap.gov
   ```

3. Verify Cloudflare proxy is active:
   ```bash
   curl -I https://gofap.gov
   # Look for "cf-ray" header
   ```

## Cloudflare Monitoring

### Key Metrics to Monitor

1. **Cache Hit Rate**: Should be > 80% for static assets
2. **Bandwidth Savings**: Track data transferred via cache
3. **Threats Blocked**: Monitor security events
4. **Response Time**: P95 should be < 500ms

### Set Up Alerts

Go to **Notifications** → **Add**:

**High Error Rate**
```
Type: HTTP Error Rate
Threshold: > 5% for 5 minutes
Notification: Email + Slack
```

**DDoS Attack**
```
Type: DDoS Attack
Threshold: Attack detected
Notification: SMS + Email
```

**SSL Certificate Expiry**
```
Type: SSL Certificate
Threshold: 14 days before expiry
Notification: Email
```

## Troubleshooting

### Issue: DNS not resolving

**Solution:**
```bash
# Check nameservers
dig NS gofap.gov

# Verify they match Cloudflare nameservers
# Should return something like:
# bob.ns.cloudflare.com
# jane.ns.cloudflare.com
```

### Issue: SSL/TLS errors

**Solution:**
1. Verify encryption mode is "Full (strict)"
2. Ensure Azure has valid SSL certificate
3. Check intermediate certificates are installed
4. Wait for SSL certificate provisioning (can take up to 24 hours)

### Issue: Cache not working

**Solution:**
```bash
# Check cache headers
curl -I https://gofap.gov/static/css/style.css

# Look for:
# CF-Cache-Status: HIT
# CF-Ray: [ray-id]
```

### Issue: Slow performance

**Solution:**
1. Enable Argo Smart Routing (paid feature)
2. Enable HTTP/3 with QUIC
3. Verify image optimization is active
4. Check if Rocket Loader is causing issues

## Cost Optimization

### Free Tier Includes:
- ✅ Unlimited DDoS mitigation
- ✅ Global CDN
- ✅ Free SSL certificates
- ✅ Basic analytics
- ✅ Page Rules (3 included)

### Pro Tier ($20/month) Adds:
- ✅ 20 Page Rules
- ✅ WAF with custom rules
- ✅ Image optimization
- ✅ Mobile optimization
- ✅ Priority support

### Business Tier ($200/month) Adds:
- ✅ 50 Page Rules
- ✅ Advanced DDoS protection
- ✅ PCI compliance
- ✅ Guaranteed 100% uptime SLA

**Recommendation**: Start with Free tier, upgrade to Pro when traffic increases.

## Security Best Practices

1. **API Token Security**
   - Use scoped API tokens (not Global API Key)
   - Rotate tokens every 90 days
   - Store in GitHub Secrets, never commit to code

2. **WAF Configuration**
   - Enable OWASP Core Ruleset
   - Create custom rules for application-specific threats
   - Monitor and adjust sensitivity

3. **Rate Limiting**
   - Implement rate limits on login endpoints
   - Protect API endpoints from abuse
   - Use Cloudflare Rate Limiting or Workers

4. **DDoS Protection**
   - Cloudflare automatically mitigates Layer 3/4 attacks
   - Configure Layer 7 rules for application-level attacks
   - Enable "I'm Under Attack" mode during active attacks

5. **Content Security**
   - Enable Hotlink Protection for images
   - Use signed URLs for sensitive content
   - Implement CSRF protection in application

## Support Resources

- **Cloudflare Community**: https://community.cloudflare.com/
- **Cloudflare Docs**: https://developers.cloudflare.com/
- **Status Page**: https://www.cloudflarestatus.com/
- **Support Portal**: https://dash.cloudflare.com/?to=/:account/support

---

**Version**: 1.0  
**Last Updated**: 2026-01-09  
**Maintained By**: DevOps Team
