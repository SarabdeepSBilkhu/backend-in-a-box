"""Auto-generated CRUD router for User."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, time
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.core.hooks import hook_registry

class UserCreate(BaseModel):
    """Pydantic schema for User create."""
    email: str
    password_hash: str
    full_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Pydantic schema for User update."""
    id: UUID | None = None
    email: str | None = None
    password_hash: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Pydantic schema for User response."""
    id: UUID
    email: str
    password_hash: str
    full_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    item: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new User."""
    # Execute before_create hooks
    data = item.model_dump()
    hook_registry.execute_hooks("before_create", "User", data=data)
    
    db_item = User(**data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Execute after_create hooks
    hook_registry.execute_hooks("after_create", "User", instance=db_item)
    
    return db_item


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all users with pagination."""
    items = db.query(User).offset(skip).limit(limit).all()
    return items


@router.get("/{id}", response_model=UserResponse)
def get_user(
    id: UUID,
    db: Session = Depends(get_db)
):
    """Get a single User by ID."""
    item = db.query(User).filter(User.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="User not found")
    return item


@router.put("/{id}", response_model=UserResponse)
def update_user(
    id: UUID,
    item_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update a User."""
    item = db.query(User).filter(User.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Store old data for audit hooks
    old_data = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
    
    # Execute before_update hooks
    update_data = item_update.model_dump(exclude_unset=True)
    hook_registry.execute_hooks("before_update", "User", instance=item, data=update_data)
    
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    # Execute after_update hooks
    hook_registry.execute_hooks("after_update", "User", instance=item, old_data=old_data)
    
    return item


@router.delete("/{id}", status_code=204)
def delete_user(
    id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a User."""
    item = db.query(User).filter(User.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Execute before_delete hooks (can abort deletion)
    should_delete = hook_registry.execute_hooks("before_delete", "User", instance=item)
    
    if should_delete is False:
        # Hook aborted deletion (e.g., soft delete)
        db.commit()  # Commit any changes made by hooks
        return None
    
    # Store instance data for after_delete hooks
    instance_data = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
    
    db.delete(item)
    db.commit()
    
    # Execute after_delete hooks
    hook_registry.execute_hooks("after_delete", "User", instance_data=instance_data)
    
    return None
