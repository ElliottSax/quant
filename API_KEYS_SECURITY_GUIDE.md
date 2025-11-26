# API Keys Security Guide

**CRITICAL**: This document contains important security information for your API keys.

---

## 🔒 Security Status

✅ **API keys added**: 12 providers configured
✅ **File permissions**: Set to 600 (owner read/write only)
✅ **.gitignore**: Updated to exclude .env files
✅ **.env.example**: Created for reference

---

## 🔑 Configured API Keys

### Active Providers (12 total)

1. ✅ **xAI (Grok)** - Configured
2. ✅ **DeepSeek** - Configured
3. ✅ **Hugging Face** - Configured
4. ✅ **Anthropic Claude** - Configured
5. ✅ **OpenRouter** - Configured (Priority #1)
6. ✅ **Google Cloud** - Configured
7. ✅ **Moonshot** - Configured
8. ✅ **Alibaba Cloud** - Configured
9. ✅ **SiliconFlow** - Configured
10. ✅ **Replicate** - Configured
11. ✅ **Fal.ai** - Configured
12. ✅ **GitHub Models** - Configured
13. ✅ **Cloudflare Workers AI** - Configured (needs account ID)

---

## ⚠️ CRITICAL SECURITY WARNINGS

### 1. File Permissions

```bash
# Verify .env is secured
ls -la quant/backend/.env
# Should show: -rw------- (600)

# If not, fix it:
chmod 600 quant/backend/.env
```

### 2. Git Protection

**NEVER commit .env to git!**

```bash
# Verify .env is ignored
git check-ignore quant/backend/.env
# Should output: quant/backend/.env

# If not:
echo "quant/backend/.env" >> .gitignore
echo "**/.env" >> .gitignore
```

### 3. Key Rotation Schedule

| Provider | Rotation Frequency | Next Rotation |
|----------|-------------------|---------------|
| Production keys | 90 days | Set reminder |
| Development keys | 180 days | Set reminder |
| Compromised keys | Immediately | N/A |

### 4. Access Control

**Who has access to these keys?**

- [ ] Document team members with access
- [ ] Restrict to necessary personnel only
- [ ] Use separate keys for dev/staging/prod
- [ ] Monitor API usage for anomalies

---

## 🔐 Best Practices

### 1. Environment Separation

```bash
# Development
quant/backend/.env.development

# Staging
quant/backend/.env.staging

# Production
quant/backend/.env.production
```

### 2. Key Storage Alternatives

**For Production**:
- [ ] Consider using **AWS Secrets Manager**
- [ ] Or **HashiCorp Vault**
- [ ] Or **Azure Key Vault**
- [ ] Or **Google Secret Manager**

### 3. Monitoring

```bash
# Set up alerts for:
- Unusual API usage patterns
- High cost spikes
- Failed authentication attempts
- Rate limit violations
```

### 4. Regular Audits

**Monthly checklist**:
- [ ] Review API usage logs
- [ ] Check cost per provider
- [ ] Verify no keys in git history
- [ ] Test key rotation process
- [ ] Update team access list

---

## 🚨 If Keys Are Compromised

### Immediate Actions

1. **Revoke compromised keys immediately**
   ```bash
   # Go to each provider's console and revoke
   ```

2. **Generate new keys**

3. **Update .env file**
   ```bash
   # Update with new keys
   vim quant/backend/.env
   ```

4. **Restart services**
   ```bash
   docker-compose restart backend
   ```

5. **Monitor for unauthorized usage**

6. **Document incident**

### Provider-Specific Revocation

| Provider | Revocation URL |
|----------|----------------|
| xAI | https://console.x.ai/team |
| DeepSeek | https://platform.deepseek.com/api_keys |
| HuggingFace | https://huggingface.co/settings/tokens |
| Anthropic | https://console.anthropic.com/settings/keys |
| OpenRouter | https://openrouter.ai/keys |
| Google Cloud | https://console.cloud.google.com/apis/credentials |
| Moonshot | https://platform.moonshot.cn/console/api-keys |
| Alibaba | https://dashscope.console.aliyun.com/ |
| SiliconFlow | https://siliconflow.cn/account/ak |
| Replicate | https://replicate.com/account/api-tokens |
| Fal.ai | https://fal.ai/dashboard/keys |
| GitHub | https://github.com/settings/tokens |
| Cloudflare | https://dash.cloudflare.com/profile/api-tokens |

---

## 💰 Cost Monitoring

### Set Up Alerts

```python
# In your application
from app.ai.providers import router

# Monitor costs
stats = router.get_all_stats()

if stats['total_cost_usd'] > 100.0:
    send_alert(f"AI costs exceeded $100: ${stats['total_cost_usd']:.2f}")
```

### Provider Billing Dashboards

| Provider | Billing URL |
|----------|-------------|
| OpenRouter | https://openrouter.ai/activity |
| DeepSeek | https://platform.deepseek.com/usage |
| Anthropic | https://console.anthropic.com/settings/billing |
| Google Cloud | https://console.cloud.google.com/billing |
| Replicate | https://replicate.com/account/billing |

---

## 🔄 Key Rotation Process

### Automated Rotation (Recommended)

```python
# rotation_script.py
import os
from datetime import datetime, timedelta

def check_key_age():
    """Check if keys need rotation"""
    last_rotation = os.getenv("LAST_KEY_ROTATION")
    if not last_rotation:
        return True

    last_date = datetime.fromisoformat(last_rotation)
    age_days = (datetime.now() - last_date).days

    return age_days > 90  # Rotate every 90 days

def rotate_keys():
    """Rotate all API keys"""
    # 1. Generate new keys from each provider
    # 2. Update .env file
    # 3. Test new keys
    # 4. Revoke old keys
    # 5. Update LAST_KEY_ROTATION
    pass

if check_key_age():
    rotate_keys()
```

---

## 📊 Usage Tracking

### Current Configuration

```bash
# Priority Order (lower = higher priority)
1. OpenRouter (5)
2. DeepSeek (10)
3. Google Cloud (15)
4. GitHub Models (20)
5. Moonshot (30)
6. Alibaba (35)
7. SiliconFlow (40)
8. HuggingFace (50)
9. Replicate (60)
10. Fal.ai (70)
11. Cloudflare (80)
```

### Monitor Usage

```bash
# View real-time stats
curl http://localhost:8000/api/v1/ai/stats

# Expected response:
{
  "total_requests": 1234,
  "total_cost_usd": 12.45,
  "providers": {
    "openrouter": {
      "requests": 800,
      "cost": 8.50,
      "success_rate": 0.95
    },
    "deepseek": {
      "requests": 434,
      "cost": 3.95,
      "success_rate": 0.98
    }
  }
}
```

---

## 🛡️ Additional Security Layers

### 1. IP Whitelisting

Some providers support IP whitelisting:
```bash
# Example: Restrict to your server IPs
Allowed IPs: 203.0.113.0/24
```

### 2. Referrer Restrictions

For browser-based APIs:
```bash
# Example: OpenRouter
HTTP-Referer: https://yourapp.com
X-Title: Quant Analytics Platform
```

### 3. Rate Limiting

```python
# Already configured in .env
OPENROUTER_RATE_LIMIT=60  # 60 requests/minute
DEEPSEEK_RATE_LIMIT=60
# ... etc
```

---

## 📝 Compliance & Audit Trail

### Logging

```python
# All API calls are logged
2025-11-17 15:30:00 - AI request: $0.0025 via openrouter
2025-11-17 15:30:05 - AI request: $0.0018 via deepseek
```

### Audit Log Location

```bash
quant/backend/logs/ai_usage.log
```

### Export Usage Report

```bash
# Monthly usage report
python scripts/export_ai_usage.py --month 2025-11
```

---

## ✅ Security Checklist

- [x] API keys added to .env
- [x] File permissions set to 600
- [x] .env added to .gitignore
- [x] .env.example created
- [ ] Set up cost alerts
- [ ] Configure billing limits on provider dashboards
- [ ] Document team access
- [ ] Set calendar reminders for key rotation
- [ ] Test key revocation process
- [ ] Set up monitoring dashboard
- [ ] Configure backup keys for critical providers
- [ ] Document incident response plan

---

## 🆘 Support Contacts

### Emergency Key Revocation

1. **Internal**: [Your DevOps team]
2. **External**: Contact each provider's support

### Security Team

- Email: security@yourcompany.com
- Slack: #security-alerts
- On-call: [Phone number]

---

## 📚 Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Cloud Security Alliance](https://cloudsecurityalliance.org/)

---

**Last Updated**: 2025-11-17
**Next Review**: 2025-12-17
**Responsible**: DevOps/Security Team
