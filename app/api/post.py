"""Auto-generated CRUD router for Post."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, time
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.models.post import Post
from app.core.hooks import hook_registry

class PostCreate(BaseModel):
    """Pydantic schema for Post create."""
    title: str
    content: str
    published: bool | None = None
    view_count: int | None = None
    
    class Config:
        from_attributes = True


class PostUpdate(BaseModel):
    """Pydantic schema for Post update."""
    id: UUID | None = None
    title: str | None = None
    content: str | None = None
    published: bool | None = None
    view_count: int | None = None
    
    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    """Pydantic schema for Post response."""
    id: UUID
    title: str
    content: str
    published: bool | None = None
    view_count: int | None = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostResponse, status_code=201)
def create_post(
    item: PostCreate,
    db: Session = Depends(get_db)
):
    """Create a new Post."""
    # Execute before_create hooks
    data = item.model_dump()
    hook_registry.execute_hooks("before_create", "Post", data=data)
    
    db_item = Post(**data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Execute after_create hooks
    hook_registry.execute_hooks("after_create", "Post", instance=db_item)
    
    return db_item


@router.get("/", response_model=List[PostResponse])
def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all posts with pagination."""
    items = db.query(Post).offset(skip).limit(limit).all()
    return items


@router.get("/{id}", response_model=PostResponse)
def get_post(
    id: UUID,
    db: Session = Depends(get_db)
):
    """Get a single Post by ID."""
    item = db.query(Post).filter(Post.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Post not found")
    return item


@router.put("/{id}", response_model=PostResponse)
def update_post(
    id: UUID,
    item_update: PostUpdate,
    db: Session = Depends(get_db)
):
    """Update a Post."""
    item = db.query(Post).filter(Post.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Store old data for audit hooks
    old_data = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
    
    # Execute before_update hooks
    update_data = item_update.model_dump(exclude_unset=True)
    hook_registry.execute_hooks("before_update", "Post", instance=item, data=update_data)
    
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    # Execute after_update hooks
    hook_registry.execute_hooks("after_update", "Post", instance=item, old_data=old_data)
    
    return item


@router.delete("/{id}", status_code=204)
def delete_post(
    id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a Post."""
    item = db.query(Post).filter(Post.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Execute before_delete hooks (can abort deletion)
    should_delete = hook_registry.execute_hooks("before_delete", "Post", instance=item)
    
    if should_delete is False:
        # Hook aborted deletion (e.g., soft delete)
        db.commit()  # Commit any changes made by hooks
        return None
    
    # Store instance data for after_delete hooks
    instance_data = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
    
    db.delete(item)
    db.commit()
    
    # Execute after_delete hooks
    hook_registry.execute_hooks("after_delete", "Post", instance_data=instance_data)
    
    return None
