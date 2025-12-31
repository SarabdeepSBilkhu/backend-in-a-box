# Database Migrations Guide

## Overview

Backend-in-a-Box uses **Alembic** for database migrations, enabling version-controlled schema evolution. Migrations auto-generate from schema changes and run automatically on deployment.

## Quick Start

### Initial Setup

```bash
# 1. Generate code from schemas
python -m generator

# 2. Initialize database
python migrate.py init

# 3. Start application
docker-compose up
```

That's it! Your database is now set up with the current schema.

## Migration Commands

### Initialize Database

```bash
python migrate.py init
```

Creates the database schema from your current models. Run this once when setting up a new environment.

### Generate Migration

```bash
python migrate.py generate "add phone number field"
```

Auto-detects changes between your models and database, creates a migration file.

### Apply Migrations

```bash
python migrate.py upgrade
```

Applies all pending migrations to the database.

### Rollback Migration

```bash
python migrate.py downgrade      # Rollback 1 migration
python migrate.py downgrade 3    # Rollback 3 migrations
```

### Check Status

```bash
python migrate.py status
```

Shows current migration version and history.

## Common Workflows

### Adding a New Field

1. **Update Schema**

   ```yaml
   # app/schema/user.yaml
   fields:
     phone_number: # NEW
       type: string
       required: false
       max_length: 20
   ```

2. **Regenerate Code**

   ```bash
   python -m generator
   ```

3. **Generate Migration**

   ```bash
   python migrate.py generate "add phone_number to user"
   ```

4. **Review Migration**

   ```bash
   # Check migrations/versions/YYYYMMDD_HHMM_*_add_phone_number_to_user.py
   ```

5. **Apply Migration**
   ```bash
   python migrate.py upgrade
   ```

### Adding a New Model

1. **Create Schema**

   ```yaml
   # app/schema/product.yaml
   name: Product
   table: products
   fields:
     id: { type: uuid, primary: true }
     name: { type: string, required: true }
     price: { type: float, required: true }
   ```

2. **Generate Code & Migration**
   ```bash
   python -m generator
   python migrate.py generate "add product model"
   python migrate.py upgrade
   ```

### Removing a Field

> [!WARNING] > **Data Loss**: Removing fields will delete data. Review migrations carefully!

1. **Remove from Schema**

   ```yaml
   # Remove the field from app/schema/user.yaml
   ```

2. **Generate Migration**

   ```bash
   python -m generator
   python migrate.py generate "remove deprecated field"
   ```

3. **Review Migration** ⚠️

   ```python
   # migrations/versions/xxx_remove_deprecated_field.py
   def upgrade():
       op.drop_column('users', 'old_field')  # Data will be lost!
   ```

4. **Apply Migration**
   ```bash
   python migrate.py upgrade
   ```

### Changing Field Type

> [!CAUTION] > **Complex Migration**: Type changes may require data transformation.

1. **Update Schema**

   ```yaml
   # Change type from string to integer
   age:
     type: integer # Was: string
   ```

2. **Generate Migration**

   ```bash
   python -m generator
   python migrate.py generate "change age to integer"
   ```

3. **Review & Modify Migration**

   ```python
   # You may need to add data transformation logic
   def upgrade():
       # Option 1: Simple type change (may fail if data incompatible)
       op.alter_column('users', 'age', type_=sa.Integer())

       # Option 2: Create new column, migrate data, drop old
       op.add_column('users', sa.Column('age_new', sa.Integer()))
       op.execute("UPDATE users SET age_new = CAST(age AS INTEGER)")
       op.drop_column('users', 'age')
       op.alter_column('users', 'age_new', new_column_name='age')
   ```

4. **Apply Migration**
   ```bash
   python migrate.py upgrade
   ```

## Docker Integration

Migrations run **automatically** when you start the application with Docker:

```bash
docker-compose up
```

**Startup sequence:**

1. Database starts
2. Entrypoint script waits for database
3. Migrations run automatically
4. Application starts

**Logs:**

```
🚀 Starting Backend-in-a-Box...
⏳ Waiting for database...
✅ Database is ready
📦 Running database migrations...
⬆️  Applying migrations...
✅ Migrations applied successfully!
🎉 Migrations complete, starting application...
```

## Migration File Structure

### Auto-Generated Migration

```python
"""add phone_number to user

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2026-01-01 03:25:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123def456'
down_revision = 'previous_revision'

def upgrade() -> None:
    """Upgrade database schema."""
    op.add_column('users',
        sa.Column('phone_number', sa.String(20), nullable=True)
    )

def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_column('users', 'phone_number')
```

### Migration Location

```
migrations/
├── env.py                    # Alembic environment config
├── script.py.mako           # Migration template
└── versions/                # Migration files
    ├── 20260101_0325_abc123_add_phone_number.py
    └── 20260101_0330_def456_add_product_model.py
```

## Best Practices

### 1. Always Review Migrations

**❌ Bad:**

```bash
python migrate.py generate "changes" && python migrate.py upgrade
```

**✅ Good:**

```bash
python migrate.py generate "add phone field"
# Review the migration file
cat migrations/versions/*_add_phone_field.py
# Then apply
python migrate.py upgrade
```

### 2. Use Descriptive Messages

**❌ Bad:**

```bash
python migrate.py generate "changes"
python migrate.py generate "update"
```

**✅ Good:**

```bash
python migrate.py generate "add phone_number to user"
python migrate.py generate "create product table"
```

### 3. Test Rollbacks

```bash
# Apply migration
python migrate.py upgrade

# Test rollback
python migrate.py downgrade

# Re-apply
python migrate.py upgrade
```

### 4. Backup Before Destructive Changes

```bash
# Before removing fields or changing types
pg_dump -U postgres backend_in_a_box > backup.sql
```

### 5. Handle Data Migrations

For complex changes, add data migration logic:

```python
def upgrade():
    # Add new column
    op.add_column('users', sa.Column('full_name', sa.String(255)))

    # Migrate data
    op.execute("""
        UPDATE users
        SET full_name = first_name || ' ' || last_name
    """)

    # Drop old columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
```

## Troubleshooting

### Migration Fails

**Error:** `Target database is not up to date`

**Solution:**

```bash
python migrate.py status  # Check current version
python migrate.py upgrade  # Apply pending migrations
```

### Conflicting Migrations

**Error:** `Multiple head revisions`

**Solution:**

```bash
alembic merge heads -m "merge migrations"
python migrate.py upgrade
```

### Reset Database (Development Only)

```bash
# Drop all tables
docker-compose down -v

# Recreate and migrate
docker-compose up
```

### Manual Migration

If auto-generation misses something:

```bash
# Create empty migration
alembic revision -m "custom change"

# Edit the file manually
# migrations/versions/xxx_custom_change.py
```

### Check Migration SQL

See what SQL will run without applying:

```bash
alembic upgrade head --sql > migration.sql
cat migration.sql
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Review all pending migrations
- [ ] Test migrations on staging database
- [ ] Backup production database
- [ ] Plan rollback strategy
- [ ] Schedule maintenance window (if needed)

### Deployment Steps

1. **Backup Database**

   ```bash
   pg_dump -h prod-db -U postgres backend_in_a_box > backup_$(date +%Y%m%d).sql
   ```

2. **Deploy New Code**

   ```bash
   git pull origin main
   docker-compose build
   ```

3. **Run Migrations**

   ```bash
   docker-compose up -d
   # Migrations run automatically via entrypoint
   ```

4. **Verify**
   ```bash
   docker-compose logs api | grep "Migrations applied"
   ```

### Rollback in Production

If deployment fails:

```bash
# Rollback code
git checkout previous_tag
docker-compose build

# Rollback migrations
docker-compose exec api python migrate.py downgrade

# Restart
docker-compose up -d
```

## Advanced Usage

### Offline Migrations

Generate SQL for manual execution:

```bash
alembic upgrade head --sql > migration.sql
# Execute migration.sql on production database
```

### Multiple Databases

Create separate Alembic configurations:

```bash
# alembic_analytics.ini
# migrations_analytics/
```

### Custom Migration Logic

```python
def upgrade():
    # Use op.execute for custom SQL
    op.execute("""
        CREATE INDEX CONCURRENTLY idx_users_email
        ON users(email)
    """)

    # Use connection for complex logic
    connection = op.get_bind()
    results = connection.execute("SELECT id FROM users")
    for row in results:
        # Process each row
        pass
```

## Migration Hooks

Integrate with the hook system:

```python
# app/services/migration_hooks.py
from app.core.hooks import after_create

@after_create("User")
def check_migration_status(instance):
    """Ensure migrations are up to date."""
    # Check alembic_version table
    pass
```

## Next Steps

- See [README.md](file:///c:/Users/sanjh/Projects/Backend-in-a-box/README.md) for overall system documentation
- Check [HOOKS.md](file:///c:/Users/sanjh/Projects/Backend-in-a-box/HOOKS.md) for hook system guide
- Review [example schemas](file:///c:/Users/sanjh/Projects/Backend-in-a-box/app/schema/) for schema format
