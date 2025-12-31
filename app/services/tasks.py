"""Background tasks for async operations."""
from app.services.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="send_email_task")
def send_email_task(to_email: str, subject: str, body: str):
    """Send an email asynchronously.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body
    """
    logger.info(f"Sending email to {to_email}: {subject}")
    # TODO: Implement actual email sending (SMTP, SendGrid, etc.)
    # For now, just log
    logger.info(f"Email sent to {to_email}")
    return {"status": "sent", "to": to_email}


@celery_app.task(name="log_audit_task")
def log_audit_task(model_name: str, instance_id: str, old_data: dict, new_data: dict):
    """Log audit trail for data changes.
    
    Args:
        model_name: Name of the model
        instance_id: ID of the instance
        old_data: Data before change
        new_data: Data after change
    """
    logger.info(f"Audit log: {model_name}#{instance_id} changed")
    logger.info(f"Old: {old_data}")
    logger.info(f"New: {new_data}")
    # TODO: Store in audit log table or external service
    return {"status": "logged", "model": model_name, "id": instance_id}


@celery_app.task(name="cleanup_task")
def cleanup_task(resource_id: str):
    """Clean up resources after deletion.
    
    Args:
        resource_id: ID of the deleted resource
    """
    logger.info(f"Cleaning up resources for {resource_id}")
    # TODO: Implement cleanup logic (delete files, clear cache, etc.)
    return {"status": "cleaned", "id": resource_id}


@celery_app.task(name="external_api_task")
def external_api_task(url: str, data: dict):
    """Make external API calls asynchronously.
    
    Args:
        url: API endpoint URL
        data: Data to send
    """
    logger.info(f"Calling external API: {url}")
    # TODO: Implement HTTP request
    return {"status": "called", "url": url}
