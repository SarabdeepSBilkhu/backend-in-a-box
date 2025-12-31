"""Example hook implementations demonstrating common patterns."""
from app.core.hooks import before_create, after_create, before_update, after_update, before_delete, after_delete
from app.services.tasks import send_email_task, log_audit_task, cleanup_task
from fastapi import HTTPException
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# USER HOOKS
# ============================================================================

@after_create("User")
def send_welcome_email(instance):
    """Send welcome email after user creation."""
    logger.info(f"Triggering welcome email for user: {instance.email}")
    send_email_task.delay(
        to_email=instance.email,
        subject="Welcome to Backend-in-a-Box!",
        body=f"Hello {instance.full_name or 'User'}, welcome to our platform!"
    )


@before_create("User")
def validate_user_email(data):
    """Validate user email before creation."""
    email = data.get("email", "")
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    # Convert email to lowercase
    data["email"] = email.lower()
    return data


@after_update("User")
def audit_user_changes(instance, old_data):
    """Log audit trail for user changes."""
    logger.info(f"User {instance.id} updated")
    log_audit_task.delay(
        model_name="User",
        instance_id=str(instance.id),
        old_data=old_data,
        new_data={
            "email": instance.email,
            "full_name": instance.full_name,
            "is_active": instance.is_active,
        }
    )


@before_delete("User")
def prevent_superuser_deletion(instance):
    """Prevent deletion of superuser accounts."""
    if getattr(instance, "is_superuser", False):
        raise HTTPException(
            status_code=403,
            detail="Cannot delete superuser accounts"
        )


# ============================================================================
# POST HOOKS
# ============================================================================

@before_create("Post")
def validate_post_content(data):
    """Validate post content before creation."""
    content = data.get("content", "")
    title = data.get("title", "")
    
    # Check for spam keywords
    spam_keywords = ["spam", "viagra", "casino"]
    if any(keyword in content.lower() or keyword in title.lower() for keyword in spam_keywords):
        raise HTTPException(status_code=400, detail="Spam content detected")
    
    # Ensure minimum content length
    if len(content) < 10:
        raise HTTPException(status_code=400, detail="Content too short (minimum 10 characters)")
    
    return data


@after_create("Post")
def notify_post_created(instance):
    """Notify when a new post is created."""
    logger.info(f"New post created: {instance.title} (ID: {instance.id})")
    # Could trigger notifications to followers, index in search, etc.


@before_update("Post")
def track_post_edits(instance, data):
    """Track when posts are edited."""
    logger.info(f"Post {instance.id} being edited")
    # Could store edit history, notify subscribers, etc.
    return data


@after_update("Post")
def reindex_post(instance, old_data):
    """Reindex post in search engine after update."""
    logger.info(f"Reindexing post {instance.id} in search")
    # TODO: Trigger search reindexing task


@before_delete("Post")
def soft_delete_post(instance):
    """Implement soft delete for posts."""
    if hasattr(instance, "deleted_at"):
        instance.deleted_at = datetime.utcnow()
        # Return False to prevent actual deletion
        # The instance will be updated instead
        logger.info(f"Soft deleting post {instance.id}")
        return False
    return True


@after_delete("Post")
def cleanup_post_resources(instance_data):
    """Clean up resources after post deletion."""
    logger.info(f"Cleaning up resources for deleted post {instance_data.get('id')}")
    cleanup_task.delay(str(instance_data.get("id")))


# ============================================================================
# GENERIC HOOKS (apply to multiple models)
# ============================================================================

def create_timestamp_hook(instance):
    """Generic hook to log creation timestamp."""
    logger.info(f"Record created at {instance.created_at}")


def update_timestamp_hook(instance, old_data):
    """Generic hook to log update timestamp."""
    logger.info(f"Record updated at {instance.updated_at}")


# Register generic hooks for both User and Post
for model in ["User", "Post"]:
    after_create(model)(create_timestamp_hook)
    after_update(model)(update_timestamp_hook)
