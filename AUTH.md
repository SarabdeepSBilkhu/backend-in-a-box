# Authentication & Authorization Guide

## Overview

Backend-in-a-Box includes a complete **JWT-based authentication system** with user registration, login, protected routes, and role-based access control (RBAC).

## Quick Start

### 1. Register a User

```bash
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 2. Login

```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### 3. Access Protected Route

```bash
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

## Authentication Endpoints

### Register

**POST** `/api/v1/auth/register`

Create a new user account.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe" // optional
}
```

**Response:** `201 Created`

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

**Errors:**

- `400` - Email already registered
- `422` - Validation error (password too short, invalid email)

---

### Login

**POST** `/api/v1/auth/login`

Authenticate with email and password.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

**Errors:**

- `401` - Incorrect email or password
- `403` - Inactive user account

---

### Get Current User

**GET** `/api/v1/auth/me`

Get current user profile.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-01T00:00:00"
}
```

---

### Update Profile

**PUT** `/api/v1/auth/me`

Update current user profile.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "full_name": "Jane Doe",
  "email": "newemail@example.com" // optional
}
```

**Response:** `200 OK` (updated user profile)

---

### Change Password

**POST** `/api/v1/auth/change-password`

Change user password.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "old_password": "OldPass123!",
  "new_password": "NewSecurePass456!"
}
```

**Response:** `204 No Content`

**Errors:**

- `400` - Incorrect old password

## Protected Routes

### Basic Protection

Require authentication for any endpoint:

```python
from fastapi import APIRouter, Depends
from app.auth import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/protected")
def protected_endpoint(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.email}"}
```

### Superuser Only

Require superuser role:

```python
from app.auth import require_superuser

@router.get("/admin")
def admin_endpoint(current_user: User = Depends(require_superuser)):
    return {"message": "Admin access granted"}
```

### Owner-Based Access

Allow users to access only their own resources:

```python
from fastapi import HTTPException
from uuid import UUID

@router.get("/posts/{post_id}")
def get_post(
    post_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")

    # Check ownership
    if post.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(403, "Not authorized")

    return post
```

## Token Management

### Token Types

**Access Token:**

- Short-lived (30 minutes)
- Used for API requests
- Include in `Authorization: Bearer <token>` header

**Refresh Token:**

- Long-lived (7 days)
- Used to get new access tokens
- Store securely (httpOnly cookie recommended)

### Token Expiration

When access token expires (401 error), use refresh token to get a new one:

```python
# Note: Refresh endpoint not yet implemented
# Will be added in future update
```

### Token Storage (Client-Side)

**Best Practice:**

- Store access token in memory (JavaScript variable)
- Store refresh token in httpOnly cookie
- Never store tokens in localStorage (XSS risk)

**For Development:**

```javascript
// Store in memory
let accessToken = response.access_token;

// Include in requests
fetch("/api/v1/auth/me", {
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
});
```

## Role-Based Access Control

### Permission Levels

| Level             | Description         | Dependency                |
| ----------------- | ------------------- | ------------------------- |
| **Public**        | No authentication   | None                      |
| **Authenticated** | Valid JWT required  | `get_current_active_user` |
| **Superuser**     | Admin access        | `require_superuser`       |
| **Owner**         | Resource owner only | Custom logic              |

### Examples

**Public Endpoint:**

```python
@router.get("/public")
def public_endpoint():
    return {"message": "Anyone can access"}
```

**Authenticated Endpoint:**

```python
@router.get("/protected")
def protected_endpoint(current_user: User = Depends(get_current_active_user)):
    return {"user": current_user.email}
```

**Admin Endpoint:**

```python
@router.get("/admin/users")
def list_all_users(
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return {"users": users}
```

## Creating a Superuser

### Via Database

```sql
UPDATE users
SET is_superuser = true
WHERE email = 'admin@example.com';
```

### Via Python Script

```python
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
import uuid

db = SessionLocal()

admin = User(
    id=uuid.uuid4(),
    email="admin@example.com",
    password_hash=get_password_hash("AdminPass123!"),
    full_name="Admin User",
    is_active=True,
    is_superuser=True
)

db.add(admin)
db.commit()
```

## Security Best Practices

### Password Requirements

- Minimum 8 characters
- Use strong passwords (mix of letters, numbers, symbols)
- Never store plain passwords
- Passwords are hashed with bcrypt (cost factor 12)

### Token Security

- Access tokens expire after 30 minutes
- Refresh tokens expire after 7 days
- Tokens are signed with SECRET_KEY
- Change SECRET_KEY in production

### HTTPS

Always use HTTPS in production:

- Prevents token interception
- Protects credentials in transit
- Required for secure cookies

## Testing Authentication

### Using Swagger UI

1. Go to `http://localhost:8000/docs`
2. Click "Authorize" button (top right)
3. Enter: `Bearer <your_access_token>`
4. Click "Authorize"
5. All protected endpoints now accessible

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Get profile (use token from login)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## Troubleshooting

### 401 Unauthorized

**Cause:** Invalid or expired token

**Solution:**

- Check token is included in Authorization header
- Verify token format: `Bearer <token>`
- Token may be expired (get new one via login)

### 403 Forbidden

**Cause:** Insufficient permissions

**Solution:**

- User account may be inactive
- Endpoint requires superuser role
- Check user permissions in database

### 400 Email Already Registered

**Cause:** Email already exists

**Solution:**

- Use different email
- Login instead of register
- Reset password if forgotten

## Integration with Hooks

Add auth-related hooks:

```python
# app/services/auth_hooks.py
from app.core.hooks import after_create
from app.services.tasks import send_email_task

@after_create("User")
def send_welcome_email(instance):
    """Send welcome email after registration."""
    send_email_task.delay(
        instance.email,
        "Welcome!",
        f"Welcome to our platform, {instance.full_name}!"
    )
```

## Next Steps

- See [HOOKS.md](file:///c:/Users/sanjh/Projects/Backend-in-a-box/HOOKS.md) for adding custom auth logic
- Check [example_protected.py](file:///c:/Users/sanjh/Projects/Backend-in-a-box/app/api/example_protected.py) for more examples
- Review [README.md](file:///c:/Users/sanjh/Projects/Backend-in-a-box/README.md) for system overview
