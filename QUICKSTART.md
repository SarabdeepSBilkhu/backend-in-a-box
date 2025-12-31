# Backend-in-a-Box Quick Start

## 🚀 Getting Started (3 Steps)

### 1. Generate Code from Schemas

```bash
python -m generator
```

### 2. Set Up Environment

```bash
# Already done - .env file created
# Edit if needed for custom database/redis URLs
```

### 3. Run with Docker

```bash
docker-compose up --build
```

**Your API is now live!**

- 📚 API Docs: http://localhost:8000/docs
- 🔧 ReDoc: http://localhost:8000/redoc
- ❤️ Health Check: http://localhost:8000/health

## 📝 What Was Generated

From your schemas (`app/schema/*.yaml`):

- ✅ SQLAlchemy models in `app/models/`
- ✅ CRUD routers in `app/api/`
- ✅ Pydantic schemas for validation
- ✅ Complete OpenAPI documentation

## 🧪 Test the API

Open http://localhost:8000/docs and try:

1. **Create a User** (POST /api/v1/users)

```json
{
  "email": "test@example.com",
  "password_hash": "hashed_password_here",
  "full_name": "Test User",
  "is_active": true
}
```

2. **List Users** (GET /api/v1/users)
3. **Create a Post** (POST /api/v1/posts)
4. **List Posts** (GET /api/v1/posts)

## 🔄 Adding New Models

1. Create a new YAML file in `app/schema/`
2. Run `python -m generator`
3. Restart the server

That's it! No manual coding required.

## 📖 Full Documentation

See [README.md](README.md) for complete documentation.
