# CLI Usage Guide

Admin command-line interface for managing the Quant Analytics Platform.

---

## Installation

```bash
cd backend
pip install -r requirements.txt
```

---

## Commands

### User Management

#### Create Superuser

Create an admin user with full privileges:

```bash
python -m app.cli create-superuser
```

**Interactive prompts:**
- Username
- Email
- Password (hidden, with confirmation)

**Example:**
```bash
$ python -m app.cli create-superuser
Username: admin
Email: admin@example.com
Password:
Repeat for confirmation:
✓ Superuser 'admin' created successfully!
  ID: 123e4567-e89b-12d3-a456-426614174000
  Email: admin@example.com
```

**Options:**
```bash
python -m app.cli create-superuser \
  --username admin \
  --email admin@example.com \
  --password SecurePassword123
```

---

#### List Users

View all users in the system:

```bash
python -m app.cli list-users
```

**Options:**
- `--limit N` - Show only N users (default: 10)
- `--active-only` - Show only active users

**Examples:**
```bash
# List all users (default limit: 10)
python -m app.cli list-users

# List 50 users
python -m app.cli list-users --limit 50

# List only active users
python -m app.cli list-users --active-only
```

**Output:**
```
Found 3 user(s):

✓ admin (admin@example.com)
  ID: 123e4567-e89b-12d3-a456-426614174000
  Role: SUPERUSER
  Created: 2025-01-15 10:30:00
  Last Login: 2025-01-15 14:25:00

✓ johndoe (john@example.com)
  ID: 456e7890-e89b-12d3-a456-426614174001
  Role: USER
  Created: 2025-01-15 11:00:00

✗ inactive_user (inactive@example.com)
  ID: 789e0123-e89b-12d3-a456-426614174002
  Role: USER
  Created: 2025-01-15 12:00:00
```

---

#### Activate User

Enable a deactivated user account:

```bash
python -m app.cli activate-user USERNAME
```

**Example:**
```bash
$ python -m app.cli activate-user johndoe
✓ User 'johndoe' activated successfully!
```

---

#### Deactivate User

Disable a user account (prevents login):

```bash
python -m app.cli deactivate-user USERNAME
```

**Example:**
```bash
$ python -m app.cli deactivate-user johndoe
✓ User 'johndoe' deactivated successfully!
```

---

#### Change Password

Reset a user's password:

```bash
python -m app.cli change-password USERNAME
```

**Interactive prompts:**
- New password (hidden, with confirmation)

**Example:**
```bash
$ python -m app.cli change-password johndoe
New password:
Repeat for confirmation:
✓ Password changed successfully for 'johndoe'!
```

**Options:**
```bash
python -m app.cli change-password johndoe --password NewSecurePass123
```

---

#### Delete User

Permanently remove a user account:

```bash
python -m app.cli delete-user USERNAME
```

**Interactive confirmation required unless `-y` flag is used.**

**Examples:**
```bash
# With confirmation prompt
python -m app.cli delete-user johndoe

# Skip confirmation (DANGEROUS!)
python -m app.cli delete-user johndoe -y
```

**Output:**
```bash
$ python -m app.cli delete-user johndoe
Are you sure you want to delete user 'johndoe' (john@example.com)? [y/N]: y
✓ User 'johndoe' deleted successfully!
```

---

### Database Management

#### Initialize Database

Create all database tables:

```bash
python -m app.cli db-init
```

**Use this for:**
- First-time setup
- Recreating tables after drops
- Development environments

**Warning:** This creates tables but doesn't run migrations. Use `db-migrate` for production.

---

#### Run Migrations

Execute pending database migrations:

```bash
python -m app.cli db-migrate
```

**This runs:** `alembic upgrade head`

**Output:**
```bash
$ python -m app.cli db-migrate
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002
✓ Database migrations completed successfully!
```

---

## Docker Usage

If running in Docker:

```bash
# Enter container
docker-compose exec backend bash

# Run commands
python -m app.cli create-superuser
python -m app.cli list-users
```

**Or directly:**
```bash
docker-compose exec backend python -m app.cli create-superuser
```

---

## Environment Variables

The CLI uses the same environment variables as the application:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/quant_db
SECRET_KEY=your-secret-key
# ... other variables from .env
```

---

## Common Workflows

### Initial Setup

```bash
# 1. Initialize database
python -m app.cli db-init

# 2. Run migrations
python -m app.cli db-migrate

# 3. Create first superuser
python -m app.cli create-superuser
```

### User Administration

```bash
# List all users
python -m app.cli list-users

# Deactivate problematic user
python -m app.cli deactivate-user spammer

# Reset forgotten password
python -m app.cli change-password johndoe

# Remove test accounts
python -m app.cli delete-user testuser1 -y
```

### Production Deployment

```bash
# Run migrations
python -m app.cli db-migrate

# Create admin account
python -m app.cli create-superuser \
  --username admin \
  --email admin@company.com

# Verify
python -m app.cli list-users --limit 1
```

---

## Error Handling

### Common Errors

**1. Database Connection Failed**
```
Error: could not connect to server
```
**Solution:** Check DATABASE_URL in .env

**2. User Already Exists**
```
Error: Username 'admin' already exists
```
**Solution:** Use different username or delete existing user

**3. Invalid Password**
```
Error: Password must contain at least one uppercase letter
```
**Solution:** Use stronger password meeting requirements

---

## Troubleshooting

### Check Database Connection

```bash
# Test connection
python -c "from app.core.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### View Help

```bash
# General help
python -m app.cli --help

# Command-specific help
python -m app.cli create-superuser --help
python -m app.cli list-users --help
```

### Enable Debug Logging

```bash
# Set DEBUG=true in .env
DEBUG=true python -m app.cli list-users
```

---

## Best Practices

### Security

1. **Never commit passwords** in scripts or documentation
2. **Use strong passwords** for production superusers
3. **Limit superuser accounts** - create only when necessary
4. **Regular audits** - periodically list and review users
5. **Deactivate instead of delete** - preserve audit trail

### Production

1. **Test in staging first** - verify commands before production
2. **Backup before bulk operations** - especially deletions
3. **Use confirmation flags carefully** - `-y` skips prompts
4. **Log all changes** - redirect output to log files
5. **Document admin actions** - maintain change log

---

## Advanced Usage

### Scripting

```bash
#!/bin/bash
# create_test_users.sh

for i in {1..10}; do
  python -m app.cli create-superuser \
    --username "testuser$i" \
    --email "test$i@example.com" \
    --password "TestPassword123"
done
```

### Bulk Operations

```bash
# List all users and save to file
python -m app.cli list-users --limit 1000 > users.txt

# Count active users
python -m app.cli list-users --active-only --limit 9999 | grep -c "✓"
```

### Integration with Monitoring

```bash
# Alert if no superusers exist
SUPERUSERS=$(python -m app.cli list-users | grep -c "SUPERUSER")
if [ "$SUPERUSERS" -eq 0 ]; then
  echo "WARNING: No superusers exist!"
  # Send alert...
fi
```

---

## API

The CLI can also be used programmatically:

```python
import asyncio
from app.cli import cli
from typer.testing import CliRunner

runner = CliRunner()

# Run command
result = runner.invoke(cli, ["list-users", "--limit", "5"])
print(result.output)
```

---

## Support

- **Issues:** https://github.com/ElliottSax/quant/issues
- **Documentation:** /docs
- **Community:** [Discord/Slack link]

---

## Version History

- **v0.1.0** - Initial CLI release
  - User management commands
  - Database operations
  - Interactive prompts
