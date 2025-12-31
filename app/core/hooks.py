"""Event hooks system for extending CRUD operations without modifying core code."""
from typing import Callable, Any, Dict, List
from collections import defaultdict
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class HookRegistry:
    """Central registry for all event hooks."""
    
    # Hook types
    BEFORE_CREATE = "before_create"
    AFTER_CREATE = "after_create"
    BEFORE_UPDATE = "before_update"
    AFTER_UPDATE = "after_update"
    BEFORE_DELETE = "before_delete"
    AFTER_DELETE = "after_delete"
    
    VALID_HOOKS = {
        BEFORE_CREATE, AFTER_CREATE,
        BEFORE_UPDATE, AFTER_UPDATE,
        BEFORE_DELETE, AFTER_DELETE
    }
    
    def __init__(self):
        """Initialize the hook registry."""
        self._hooks: Dict[str, Dict[str, List[Callable]]] = defaultdict(lambda: defaultdict(list))
        self._lock = Lock()
    
    def register(self, hook_type: str, model_name: str, func: Callable) -> None:
        """Register a hook function.
        
        Args:
            hook_type: Type of hook (before_create, after_create, etc.)
            model_name: Name of the model this hook applies to
            func: Hook function to execute
        """
        if hook_type not in self.VALID_HOOKS:
            raise ValueError(f"Invalid hook type: {hook_type}. Valid types: {self.VALID_HOOKS}")
        
        with self._lock:
            self._hooks[model_name][hook_type].append(func)
            logger.info(f"Registered {hook_type} hook for {model_name}: {func.__name__}")
    
    def get_hooks(self, hook_type: str, model_name: str) -> List[Callable]:
        """Get all hooks for a specific type and model.
        
        Args:
            hook_type: Type of hook
            model_name: Name of the model
            
        Returns:
            List of hook functions
        """
        return self._hooks.get(model_name, {}).get(hook_type, [])
    
    def execute_hooks(self, hook_type: str, model_name: str, **context) -> Any:
        """Execute all hooks for a specific type and model.
        
        Args:
            hook_type: Type of hook
            model_name: Name of the model
            **context: Context data passed to hooks
            
        Returns:
            Modified context or None
        """
        hooks = self.get_hooks(hook_type, model_name)
        
        if not hooks:
            return context
        
        logger.debug(f"Executing {len(hooks)} {hook_type} hook(s) for {model_name}")
        
        for hook in hooks:
            try:
                result = hook(**context)
                # If hook returns data, update context
                if result is not None:
                    if isinstance(result, dict):
                        context.update(result)
                    else:
                        # For before_delete hooks, False means abort deletion
                        return result
            except Exception as e:
                logger.error(f"Error in {hook_type} hook {hook.__name__} for {model_name}: {e}")
                raise
        
        return context
    
    def list_hooks(self) -> Dict[str, Dict[str, List[str]]]:
        """List all registered hooks.
        
        Returns:
            Dictionary of model -> hook_type -> [function_names]
        """
        result = {}
        for model_name, hooks_by_type in self._hooks.items():
            result[model_name] = {}
            for hook_type, funcs in hooks_by_type.items():
                result[model_name][hook_type] = [f.__name__ for f in funcs]
        return result


# Global hook registry instance
hook_registry = HookRegistry()


# Decorator functions for easy hook registration

def before_create(model_name: str):
    """Decorator to register a before_create hook.
    
    Hook signature: func(data: dict) -> dict | None
    - Can modify data before creation
    - Can raise exceptions to abort creation
    
    Example:
        @before_create("User")
        def validate_email(data):
            if not data.get("email"):
                raise ValueError("Email required")
    """
    def decorator(func: Callable) -> Callable:
        hook_registry.register(HookRegistry.BEFORE_CREATE, model_name, func)
        return func
    return decorator


def after_create(model_name: str):
    """Decorator to register an after_create hook.
    
    Hook signature: func(instance: Model) -> None
    - Receives the created instance
    - Cannot modify the instance (already committed)
    - Use for notifications, logging, etc.
    
    Example:
        @after_create("User")
        def send_welcome_email(instance):
            send_email_task.delay(instance.email, "Welcome!")
    """
    def decorator(func: Callable) -> Callable:
        hook_registry.register(HookRegistry.AFTER_CREATE, model_name, func)
        return func
    return decorator


def before_update(model_name: str):
    """Decorator to register a before_update hook.
    
    Hook signature: func(instance: Model, data: dict) -> dict | None
    - Receives existing instance and update data
    - Can modify data before update
    - Can raise exceptions to abort update
    
    Example:
        @before_update("User")
        def prevent_email_change(instance, data):
            if "email" in data and data["email"] != instance.email:
                raise ValueError("Cannot change email")
    """
    def decorator(func: Callable) -> Callable:
        hook_registry.register(HookRegistry.BEFORE_UPDATE, model_name, func)
        return func
    return decorator


def after_update(model_name: str):
    """Decorator to register an after_update hook.
    
    Hook signature: func(instance: Model, old_data: dict) -> None
    - Receives updated instance and old data
    - Use for audit logging, notifications, etc.
    
    Example:
        @after_update("User")
        def audit_changes(instance, old_data):
            log_audit_task.delay("User", instance.id, old_data, instance.__dict__)
    """
    def decorator(func: Callable) -> Callable:
        hook_registry.register(HookRegistry.AFTER_UPDATE, model_name, func)
        return func
    return decorator


def before_delete(model_name: str):
    """Decorator to register a before_delete hook.
    
    Hook signature: func(instance: Model) -> bool | None
    - Receives instance to be deleted
    - Return False to abort deletion (e.g., for soft delete)
    - Can raise exceptions to abort deletion
    
    Example:
        @before_delete("Post")
        def soft_delete(instance):
            instance.deleted_at = datetime.utcnow()
            return False  # Prevent actual deletion
    """
    def decorator(func: Callable) -> Callable:
        hook_registry.register(HookRegistry.BEFORE_DELETE, model_name, func)
        return func
    return decorator


def after_delete(model_name: str):
    """Decorator to register an after_delete hook.
    
    Hook signature: func(instance_data: dict) -> None
    - Receives dictionary of deleted instance data
    - Use for cleanup, logging, etc.
    
    Example:
        @after_delete("User")
        def cleanup_user_data(instance_data):
            cleanup_task.delay(instance_data["id"])
    """
    def decorator(func: Callable) -> Callable:
        hook_registry.register(HookRegistry.AFTER_DELETE, model_name, func)
        return func
    return decorator
