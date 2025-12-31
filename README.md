### 1. Install Dependencies

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Define Your Schema

Create YAML files in `app/schema/`:

```yaml
# app/schema/user.yaml
name: User
table: users
fields:
  id:
    type: uuid
    primary: true
  email:
    type: string
    unique: true
    required: true
  password_hash:
    type: string
relations: []
timestamps: true
```

### 4. Generate Code

```bash
python -m generator
```

This generates:

- SQLAlchemy models in `app/models/`
- CRUD routers in `app/api/`
- Pydantic schemas for validation

### 5. Run with Docker

```bash
docker-compose up
```

Your API is now live at `http://localhost:8000`

- 📚 API Docs: `http://localhost:8000/docs`
- 🔧 ReDoc: `http://localhost:8000/redoc`

## 📁 Repository Structure

```
backend-in-a-box/
├── app/
│   ├── core/           # Config, security, database
│   ├── schema/         # User-defined YAML schemas
│   ├── models/         # Auto-generated SQLAlchemy models
│   ├── api/            # Auto-generated CRUD routers
│   ├── services/       # Background tasks, business hooks
│   ├── auth/           # Auth flows
│   └── main.py         # FastAPI application
├── generator/
│   ├── parser.py       # Schema → AST
│   ├── model_gen.py    # AST → SQLAlchemy
│   ├── api_gen.py      # AST → CRUD routers
│   └── validator.py    # Schema validation
├── migrations/         # Alembic migrations
├── docker/
│   └── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## 🔧 Stack

**Backend:**

- Python 3.11
- FastAPI (request lifecycle, validation, OpenAPI)
- SQLAlchemy 2.0 (ORM + migrations)
- PostgreSQL (default, swappable)
- Alembic (schema migrations)

**Infrastructure:**

- Docker + Docker Compose
- Gunicorn + Uvicorn workers
- Environment-based config

**Background Tasks:**

- Celery + Redis

**Auth:**

- JWT (access + refresh tokens)
- Password hashing with bcrypt

## 📝 Schema Format

### Field Types

- `string`, `integer`, `float`, `boolean`
- `datetime`, `date`, `time`
- `uuid`, `text`, `json`, `binary`

### Field Options

- `primary`: Primary key
- `unique`: Unique constraint
- `required`: Not nullable
- `default`: Default value
- `max_length`: String max length
- `index`: Create index

### Relationships

```yaml
relations:
  - type: one_to_many
    target: Post
    back_populates: user
  - type: many_to_one
    target: Category
    foreign_key: categories.id
```

### Features

- `timestamps: true` - Auto-add `created_at` and `updated_at`
- `soft_delete: true` - Add `deleted_at` for soft deletes

## 🔌 Generated CRUD Endpoints

For each model, you automatically get:

```
POST   /{table}        # Create
GET    /{table}        # List (with pagination)
GET    /{table}/{id}   # Get by ID
PUT    /{table}/{id}   # Update
DELETE /{table}/{id}   # Delete
```

All endpoints include:

- ✅ Automatic validation (Pydantic)
- ✅ Pagination (skip/limit)
- ✅ Proper error handling
- ✅ OpenAPI documentation

## 🎨 Extension Mechanism

Custom logic lives in `services/` and `hooks/` - **never modify core**.

```python
# Example: services/user_hooks.py
@after_create("User")
def send_welcome_email(user):
    # Your custom logic
    pass
```

Events:

- `before_create`, `after_create`
- `before_update`, `after_update`
- `before_delete`, `after_delete`

## 🐳 Deployment

### Local Development

```bash
docker-compose up
```

### Production

Set environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret (generate with `openssl rand -hex 32`)
- `ENV=production`

## 📊 Example Workflow

1. **Define schema** (`app/schema/product.yaml`)
2. **Run generator** (`python -m generator`)
3. **Start server** (`docker-compose up`)
4. **Access API** (`http://localhost:8000/docs`)
5. **Extend** (add hooks in `services/`)

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app
```

## 📜 License

MIT

## 🤝 Contributing

This is an opinionated framework. Before contributing, ensure changes align with the core philosophy: **eliminate backend setup, not explore frameworks**.
