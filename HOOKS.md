# Hook System Guide

## Overview

Backend-in-a-Box includes a powerful **event hooks system** that lets you add custom business logic without modifying auto-generated code. Hooks execute before/after CRUD operations, enabling:

- ✅ Data validation
- ✅ Email notifications
- ✅ Audit logging
- ✅ Soft deletes
- ✅ External API calls
- ✅ Cache invalidation
- ✅ Search indexing

## Available Hook Types

### Before Hooks (Can Modify or Abort)

- **`before_create`**: Runs before creating a record
  - Can modify data
  - Can raise exceptions to abort creation
- **`before_update`**: Runs before updating a record
  - Can modify update data
  - Can raise exceptions to abort update
- **`before_delete`**: Runs before deleting a record
  - Return `False` to abort deletion (useful for soft delete)
  - Can raise exceptions to abort deletion

### After Hooks (Read-Only, for Side Effects)

- **`after_create`**: Runs after creating a record
  - Receives the created instance
  - Use for notifications, logging, indexing
- **`after_update`**: Runs after updating a record
  - Receives updated instance and old data
  - Use for audit trails, cache invalidation
- **`after_delete`**: Runs after deleting a record
  - Receives dictionary of deleted instance data
  - Use for cleanup, logging

## Quick Start

### 1. Create a Hook File

Create a Python file in `app/services/` (e.g., `app/services/my_hooks.py`):

```python
from app.core.hooks import after_create
from app.services.tasks import send_email_task

@after_create("User")
def send_welcome_email(instance):
    """Send welcome email when user is created."""
    send_email_task.delay(
        to_email=instance.email,
        subject="Welcome!",
        body=f"Hello {instance.full_name}!"
    )
```

### 2. Restart the Server

Hooks are auto-discovered at startup. Just restart:

```bash
docker-compose restart api
```

### 3. Test Your Hook

Create a user via the API and watch your hook execute!

## Hook Signatures

### before_create

```python
@before_create("ModelName")
def my_hook(data: dict) -> dict | None:
    """
    Args:
        data: Dictionary of field values to be created

    Returns:
        Modified data dict (optional)
        Can raise HTTPException to abort
    """
    # Modify data
    data["email"] = data["email"].lower()
    return data
```

### after_create

```python
@after_create("ModelName")
def my_hook(instance: Model) -> None:
    """
    Args:
        instance: The created database instance

    Note: Instance is already committed, don't modify it
    """
    send_email_task.delay(instance.email, "Created!")
```

### before_update

```python
@before_update("ModelName")
def my_hook(instance: Model, data: dict) -> dict | None:
    """
    Args:
        instance: Existing database instance
        data: Dictionary of fields being updated

    Returns:
        Modified data dict (optional)
        Can raise HTTPException to abort
    """
    if "email" in data:
        raise HTTPException(400, "Cannot change email")
```

### after_update

```python
@after_update("ModelName")
def my_hook(instance: Model, old_data: dict) -> None:
    """
    Args:
        instance: Updated database instance
        old_data: Dictionary of old field values
    """
    log_audit_task.delay("ModelName", instance.id, old_data, instance.__dict__)
```

### before_delete

```python
@before_delete("ModelName")
def my_hook(instance: Model) -> bool | None:
    """
    Args:
        instance: Instance to be deleted

    Returns:
        False to abort deletion (e.g., for soft delete)
        Can raise HTTPException to abort
    """
    # Soft delete
    instance.deleted_at = datetime.utcnow()
    return False  # Prevent actual deletion
```

### after_delete

```python
@after_delete("ModelName")
def my_hook(instance_data: dict) -> None:
    """
    Args:
        instance_data: Dictionary of deleted instance fields
    """
    cleanup_task.delay(instance_data["id"])
```

## Example Use Cases

### Email Notification

```python
from app.core.hooks import after_create
from app.services.tasks import send_email_task

@after_create("User")
def welcome_email(instance):
    send_email_task.delay(
        instance.email,
        "Welcome to our platform!",
        f"Hi {instance.full_name}, thanks for joining!"
    )
```

### Data Validation

```python
from app.core.hooks import before_create
from fastapi import HTTPException

@before_create("Post")
def validate_content(data):
    if len(data.get("content", "")) < 10:
        raise HTTPException(400, "Content too short")

    # Check for spam
    if "spam" in data["content"].lower():
        raise HTTPException(400, "Spam detected")

    return data
```

### Audit Logging

```python
from app.core.hooks import after_update
from app.services.tasks import log_audit_task

@after_update("User")
def audit_changes(instance, old_data):
    log_audit_task.delay(
        model_name="User",
        instance_id=str(instance.id),
        old_data=old_data,
        new_data={k: v for k, v in instance.__dict__.items() if not k.startswith('_')}
    )
```

### Soft Delete

```python
from app.core.hooks import before_delete
from datetime import datetime

@before_delete("Post")
def soft_delete(instance):
    instance.deleted_at = datetime.utcnow()
    return False  # Prevent actual deletion
```

### Prevent Deletion

```python
from app.core.hooks import before_delete
from fastapi import HTTPException

@before_delete("User")
def prevent_admin_deletion(instance):
    if instance.is_superuser:
        raise HTTPException(403, "Cannot delete admin users")
```

### Cache Invalidation

```python
from app.core.hooks import after_update, after_delete

@after_update("Product")
def invalidate_cache(instance, old_data):
    cache.delete(f"product:{instance.id}")

@after_delete("Product")
def invalidate_cache_on_delete(instance_data):
    cache.delete(f"product:{instance_data['id']}")
```

## Best Practices

### 1. Keep Hooks Fast (Use Async Tasks)

**❌ Bad** (blocks request):

```python
@after_create("User")
def slow_hook(instance):
    send_actual_email(instance.email)  # Blocks for 2-3 seconds
```

**✅ Good** (dispatches to background):

```python
@after_create("User")
def fast_hook(instance):
    send_email_task.delay(instance.email)  # Returns immediately
```

### 2. Handle Errors Gracefully

```python
@after_create("User")
def safe_hook(instance):
    try:
        risky_operation(instance)
    except Exception as e:
        logger.error(f"Hook failed: {e}")
        # Don't raise - let the request succeed
```

### 3. Use Before Hooks for Validation

```python
@before_create("Post")
def validate(data):
    if not data.get("title"):
        raise HTTPException(400, "Title required")
    return data
```

### 4. Use After Hooks for Side Effects

```python
@after_create("Order")
def notify_warehouse(instance):
    notify_warehouse_task.delay(instance.id)
```

### 5. Don't Modify Instances in After Hooks

After hooks run AFTER the database commit. Modifying instances won't persist:

**❌ Bad**:

```python
@after_create("User")
def bad_hook(instance):
    instance.email = "changed@example.com"  # Won't persist!
```

**✅ Good**:

```python
@before_create("User")
def good_hook(data):
    data["email"] = data["email"].lower()  # Will persist
    return data
```

## Testing Hooks

### Manual Testing

1. Start the server:

   ```bash
   docker-compose up
   ```

2. Check startup logs for registered hooks:

   ```
   🎣 Registered hooks:
      User.before_create: validate_user_email
      User.after_create: send_welcome_email, create_timestamp_hook
      User.after_update: audit_user_changes, update_timestamp_hook
   ```

3. Test via Swagger UI at `http://localhost:8000/docs`

### Programmatic Testing

```python
from app.core.hooks import hook_registry

# List all hooks
hooks = hook_registry.list_hooks()
print(hooks)

# Execute hooks manually (for testing)
hook_registry.execute_hooks(
    "before_create",
    "User",
    data={"email": "test@example.com"}
)
```

## Hook Execution Order

Multiple hooks for the same event execute in **registration order**:

```python
@after_create("User")
def first_hook(instance):
    print("1")

@after_create("User")
def second_hook(instance):
    print("2")

# Output when user created: 1, 2
```

## Debugging Hooks

Enable debug logging to see hook execution:

```python
import logging
logging.getLogger("app.core.hooks").setLevel(logging.DEBUG)
```

You'll see:

```
DEBUG:app.core.hooks:Executing 2 after_create hook(s) for User
INFO:app.core.hooks:Registered after_create hook for User: send_welcome_email
```

## Advanced: Generic Hooks

Register the same hook for multiple models:

```python
def log_creation(instance):
    logger.info(f"Created {type(instance).__name__} #{instance.id}")

# Register for multiple models
for model in ["User", "Post", "Comment"]:
    after_create(model)(log_creation)
```

## Troubleshooting

### Hook Not Executing

1. Check hook is registered:

   ```bash
   # Look for hook in startup logs
   docker-compose logs api | grep "Registered"
   ```

2. Verify hook file is in `app/services/`
3. Ensure hook file doesn't start with `_`
4. Restart the server

### Hook Causing Errors

Check logs:

```bash
docker-compose logs api
```

Hooks that raise exceptions will:

- Roll back the database transaction
- Return error to client
- Log the error

### Celery Tasks Not Running

1. Check Celery worker is running:

   ```bash
   docker-compose ps celery_worker
   ```

2. Check worker logs:

   ```bash
   docker-compose logs celery_worker
   ```

3. Verify Redis is accessible:
   ```bash
   docker-compose ps redis
   ```

## Next Steps

- See [example_hooks.py](file:///c:/Users/sanjh/Projects/Backend-in-a-box/app/services/example_hooks.py) for more examples
- Check [tasks.py](file:///c:/Users/sanjh/Projects/Backend-in-a-box/app/services/tasks.py) for background task templates
- Read [README.md](file:///c:/Users/sanjh/Projects/Backend-in-a-box/README.md) for overall system documentation
