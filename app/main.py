"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import services to trigger hook auto-discovery
import app.services  # noqa

# Import generated routers
try:
    from app.api import api_router
except ImportError:
    # Routers not generated yet
    api_router = None

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Backend-in-a-Box API",
        "docs": "/docs",
        "version": "0.1.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Mount auth router
from app.auth import auth_router
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)

# Mount generated API routers
if api_router:
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("🚀 Backend-in-a-Box starting up...")
    print(f"📚 API docs available at: /docs")
    print(f"🔧 Environment: {settings.ENV}")
    
    # Log registered hooks
    from app.core.hooks import hook_registry
    hooks = hook_registry.list_hooks()
    if hooks:
        print(f"🎣 Registered hooks:")
        for model_name, hook_types in hooks.items():
            for hook_type, funcs in hook_types.items():
                print(f"   {model_name}.{hook_type}: {', '.join(funcs)}")
    else:
        print("⚠️  No hooks registered")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("👋 Backend-in-a-Box shutting down...")
