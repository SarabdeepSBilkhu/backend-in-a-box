"""Services package - auto-discovers and registers all hooks."""
import logging
from pathlib import Path
import importlib

logger = logging.getLogger(__name__)

# Auto-discover and import all hook modules
services_dir = Path(__file__).parent

for file_path in services_dir.glob("*.py"):
    if file_path.name.startswith("_"):
        continue  # Skip __init__.py and __pycache__
    
    if file_path.name in ["celery_app.py", "tasks.py"]:
        continue  # Skip non-hook modules
    
    module_name = f"app.services.{file_path.stem}"
    try:
        importlib.import_module(module_name)
        logger.info(f"Loaded hook module: {module_name}")
    except Exception as e:
        logger.error(f"Failed to load hook module {module_name}: {e}")

logger.info("Hook auto-discovery complete")
