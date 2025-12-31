# Getting Started with Backend-in-a-Box

## 🚀 Quick Start (2 Steps - Docker Only!)

### Prerequisites

- **Docker Desktop** installed and running

That's it! Docker handles everything else.

### Step 1: Generate Code from Schemas

```bash
# Navigate to project directory
cd c:\Path\To\Backend-in-a-box

# Generate models and APIs from YAML schemas
python -m generator
```

**Don't have Python?** No problem - skip to Step 2, Docker will generate code automatically.

### Step 2: Start with Docker

```bash
# Generate SQLAlchemy models and CRUD APIs from YAML schemas
python -m generator
```

**Expected output:**

```
🚀 Starting code generation...
📖 Parsing schemas from app/schema...
   Found 2 schema(s): User, Post
✅ Validating schemas...
   All schemas valid!
🏗️  Generating SQLAlchemy models in app/models...
   Generated 2 model file(s)
🌐 Generating CRUD routers in app/api...
   Generated 2 router file(s)
✨ Code generation complete!
```

### Step 3: Start Everything with Docker

```bash
# Start all services (database, Redis, API, Celery worker)
docker-compose up --build
```

**What happens:**

1. PostgreSQL database starts
2. Redis starts
3. Database migrations run automatically
4. Hooks are discovered and registered
5. API starts at http://localhost:8000

**You're done!** 🎉

## 📚 Access the API

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Test the API

### 1. Register a User

Go to http://localhost:8000/docs and try:

**POST** `/api/v1/auth/register`

```json
{
  "email": "test@example.com",
  "password": "SecurePass123!",
  "full_name": "Test User"
}
```

**Response:** You'll get access and refresh tokens.

### 2. Login

**POST** `/api/v1/auth/login`

```json
{
  "email": "test@example.com",
  "password": "SecurePass123!"
}
```

### 3. Access Protected Route

1. Click the **Authorize** button in Swagger UI (top right)
2. Enter: `Bearer <your_access_token>`
3. Click **Authorize**

Now try:

**GET** `/api/v1/auth/me` - Returns your user profile

### 4. Create a Post

**POST** `/api/v1/posts`

```json
{
  "title": "My First Post",
  "content": "This is my first post!",
  "published": true
}
```

### 5. List Posts

**GET** `/api/v1/posts` - Returns all posts with pagination

## 📁 Project Structure

```
backend-in-a-box/
├── app/
│   ├── schema/          # ← EDIT THESE: Define your data models in YAML
│   │   ├── user.yaml
│   │   └── post.yaml
│   ├── services/        # ← ADD HOOKS HERE: Custom business logic
│   │   └── example_hooks.py
│   ├── models/          # ← AUTO-GENERATED: Don't edit
│   ├── api/             # ← AUTO-GENERATED: Don't edit
│   └── main.py
├── migrations/          # Database migration files
├── docker-compose.yml   # Docker configuration
└── migrate.py           # Migration CLI tool
```

## 🔄 Common Workflows

### Add a New Field to User

1. **Edit schema:**

   ```yaml
   # app/schema/user.yaml
   fields:
     phone_number: # NEW FIELD
       type: string
       max_length: 20
   ```

2. **Regenerate code:**

   ```bash
   python -m generator
   ```

3. **Create migration:**

   ```bash
   python migrate.py generate "add phone_number to user"
   ```

4. **Apply migration:**

   ```bash
   python migrate.py upgrade
   ```

5. **Restart API:**
   ```bash
   docker-compose restart api
   ```

### Add a New Model

1. **Create schema file:**

   ```yaml
   # app/schema/product.yaml
   name: Product
   table: products
   fields:
     id: { type: uuid, primary: true }
     name: { type: string, required: true }
     price: { type: float, required: true }
   timestamps: true
   ```

2. **Generate & migrate:**

   ```bash
   python -m generator
   python migrate.py generate "add product model"
   python migrate.py upgrade
   docker-compose restart api
   ```

3. **Done!** Full CRUD API at `/api/v1/products`

### Add Custom Business Logic

1. **Create hook file:**

   ```python
   # app/services/my_hooks.py
   from app.core.hooks import after_create
   from app.services.tasks import send_email_task

   @after_create("User")
   def send_welcome_email(instance):
       send_email_task.delay(instance.email, "Welcome!", "...")
   ```

2. **Restart API:**
   ```bash
   docker-compose restart api
   ```

Hooks are auto-discovered and execute automatically!

## 🛠️ Useful Commands

### Development

```bash
# Generate code from schemas
python -m generator

# Initialize database
python migrate.py init

# Create migration
python migrate.py generate "description"

# Apply migrations
python migrate.py upgrade

# Rollback migration
python migrate.py downgrade

# Check migration status
python migrate.py status
```

### Docker

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Restart specific service
docker-compose restart api
```

### Database

```bash
# Access PostgreSQL
docker-compose exec db psql -U postgres -d backend_in_a_box

# Backup database
docker-compose exec db pg_dump -U postgres backend_in_a_box > backup.sql

# Reset database (CAUTION: deletes all data)
docker-compose down -v
docker-compose up
```

## 🐛 Troubleshooting

### "User model not generated"

**Solution:**

```bash
python -m generator
docker-compose restart api
```

### Port 8000 already in use

**Solution:**

```bash
# Stop other services using port 8000
# Or change port in docker-compose.yml
```

### Migrations not running

**Solution:**

```bash
# Check database is running
docker-compose ps

# Run migrations manually
docker-compose exec api python migrate.py upgrade
```

### Hooks not executing

**Solution:**

```bash
# Check startup logs for hook registration
docker-compose logs api | grep "Registered hooks"

# Ensure hook file is in app/services/
# Restart API
docker-compose restart api
```

## 📖 Next Steps

- **Read [README.md](README.md)** - System overview and architecture
- **Check [AUTH.md](AUTH.md)** - Authentication guide
- **Explore [HOOKS.md](HOOKS.md)** - Hook system documentation
- **Review [MIGRATIONS.md](MIGRATIONS.md)** - Database migration workflows

## 💡 Tips

1. **Always run `python -m generator` after changing schemas**
2. **Create migrations after generating code**
3. **Use Swagger UI** (http://localhost:8000/docs) for testing
4. **Check logs** with `docker-compose logs -f api`
5. **Don't edit generated files** in `app/models/` or `app/api/`

## 🎯 What You Get

- ✅ Auto-generated CRUD APIs
- ✅ JWT authentication (register, login, protected routes)
- ✅ Database migrations (Alembic)
- ✅ Event hooks for custom logic
- ✅ Background tasks (Celery)
- ✅ OpenAPI documentation
- ✅ Docker deployment

**From schema to production-ready API in minutes!**
