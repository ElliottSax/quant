# 📝 Credentials Checklist
## Gather These Before Deploying

Copy this file and fill in your credentials from each service.

---

## 🔐 Required Credentials

### 1. Supabase (PostgreSQL Database)
**Get from**: https://supabase.com/dashboard → Your Project → Settings → Database

```bash
# Connection String (URI format)
DATABASE_URL="postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres"

# Example:
# DATABASE_URL="postgresql://postgres.abcdefghijklmnop:your-password@aws-0-us-west-1.pooler.supabase.com:5432/postgres"
```

**Steps to get:**
1. Go to Supabase dashboard
2. Click your project
3. Settings → Database
4. Scroll to "Connection string" section
5. Select "URI" tab
6. Copy the string
7. Replace `[YOUR-PASSWORD]` with your actual database password

---

### 2. Upstash (Redis Cache)
**Get from**: https://console.upstash.com → Your Database → Details

```bash
# Redis URL (with TLS - starts with rediss://)
REDIS_URL="rediss://default:[PASSWORD]@[ENDPOINT]:6379"

# Example:
# REDIS_URL="rediss://default:AYNzAAIncDE0NGU1MGM5OTg5YmY0YmE0OWFkMDI3ZjdiYWI2NTNlMXAxMA@us1-gentle-possum-12345.upstash.io:6379"
```

**Steps to get:**
1. Go to Upstash console
2. Click your database
3. Scroll to "REST API" section
4. Copy the full Redis URL (starts with `rediss://`)

---

### 3. Cloudflare R2 (Object Storage)
**Get from**: https://dash.cloudflare.com → R2 → Manage R2 API Tokens

```bash
# R2 Credentials
AWS_ACCESS_KEY_ID="your-access-key-id"
AWS_SECRET_ACCESS_KEY="your-secret-access-key"
AWS_S3_ENDPOINT_URL="https://[ACCOUNT-ID].r2.cloudflarestorage.com"

# Example:
# AWS_ACCESS_KEY_ID="a1b2c3d4e5f6g7h8i9j0"
# AWS_SECRET_ACCESS_KEY="k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6"
# AWS_S3_ENDPOINT_URL="https://abc123def456.r2.cloudflarestorage.com"
```

**Steps to get:**
1. Go to Cloudflare dashboard
2. R2 → Manage R2 API Tokens
3. Click "Create API Token"
4. Name: `quant-backend`
5. Permissions: Object Read & Write
6. Copy Access Key ID and Secret Access Key
7. For endpoint URL: R2 → Overview → copy your account ID
8. Format: `https://[YOUR-ACCOUNT-ID].r2.cloudflarestorage.com`

---

### 4. Secret Key (Generate New)
**Generate with**:

```bash
# Run this command to generate a secure secret key
openssl rand -base64 32
```

```bash
SECRET_KEY="your-generated-secret-key-here"

# Example (yours will be different):
# SECRET_KEY="wR33Elo9wMAOIOHxyToVy8RE7c83SFuW6J0kfeY_jMo"
```

---

## 📋 Optional Credentials

### 5. Sentry (Error Tracking) - OPTIONAL
**Get from**: https://sentry.io → Settings → Projects → Client Keys

```bash
# Sentry DSN (optional but recommended)
SENTRY_DSN="https://[KEY]@[ORG].ingest.sentry.io/[PROJECT]"

# Example:
# SENTRY_DSN="https://abc123def456@o123456.ingest.sentry.io/789012"
```

**Steps to get:**
1. Go to Sentry dashboard
2. Create new project (Python / FastAPI)
3. Copy DSN from project settings

---

## ✅ Credential Summary

Once you have all credentials, you'll have:

```bash
# Required (4 items):
✅ DATABASE_URL          # From Supabase
✅ REDIS_URL             # From Upstash
✅ AWS_ACCESS_KEY_ID     # From Cloudflare R2
✅ AWS_SECRET_ACCESS_KEY # From Cloudflare R2
✅ AWS_S3_ENDPOINT_URL   # From Cloudflare R2
✅ SECRET_KEY            # Generated with openssl

# Optional (1 item):
⚪ SENTRY_DSN            # From Sentry (optional)
```

---

## 🚀 Ready to Deploy?

Once you've filled in all the credentials above, you're ready to run:

```bash
./deploy-free-tier.sh
```

The script will prompt you for these credentials during deployment.

**Pro Tip**: Keep this file handy (but don't commit it to git!) for easy copy-paste during deployment.

---

## 🔒 Security Notes

**DO NOT:**
- ❌ Commit this file to git if you fill in real credentials
- ❌ Share credentials publicly
- ❌ Use the same credentials for different environments

**DO:**
- ✅ Keep credentials in a password manager
- ✅ Use different credentials for dev/prod
- ✅ Rotate credentials periodically
- ✅ Delete this file after deployment (credentials will be in Railway/Vercel)

---

## 📞 Need Help Getting Credentials?

### Supabase Issues:
- Can't find connection string? → Settings → Database → Connection string → URI tab
- Connection refused? → Make sure you're using the "Pooler" connection string

### Upstash Issues:
- Wrong format? → Must start with `rediss://` (with double 's')
- Connection timeout? → Check if TLS is enabled (should be by default)

### Cloudflare R2 Issues:
- No R2 access? → Make sure R2 is enabled in your account (free)
- Can't create token? → Check account permissions
- Wrong endpoint? → Should be `https://[account-id].r2.cloudflarestorage.com`

### Secret Key Issues:
- Don't have openssl? → Use online generator: https://generate-secret.vercel.app/32
- Too short? → Must be at least 32 characters

---

**Next Step**: Run `./deploy-free-tier.sh` with these credentials ready! 🚀
