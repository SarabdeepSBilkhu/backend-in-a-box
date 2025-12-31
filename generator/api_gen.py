"""API generator - creates CRUD routers from schema definitions."""
from pathlib import Path
from generator.parser import SchemaDefinition, FieldDefinition


class APIGenerator:
    """Generates FastAPI CRUD routers from schema definitions."""
    
    def __init__(self, output_dir: Path | str):
        """Initialize generator with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_python_type(self, field: FieldDefinition) -> str:
        """Convert field type to Python type hint."""
        type_map = {
            "string": "str",
            "integer": "int",
            "float": "float",
            "boolean": "bool",
            "datetime": "datetime",
            "date": "date",
            "time": "time",
            "uuid": "UUID",
            "text": "str",
            "json": "dict",
            "binary": "bytes",
        }
        python_type = type_map.get(field.type, "str")
        
        if field.nullable and not field.primary:
            return f"{python_type} | None"
        return python_type
    
    def _generate_pydantic_schema(self, schema: SchemaDefinition, fields: list[FieldDefinition], schema_type: str) -> str:
        """Generate Pydantic schema for request/response."""
        field_lines = []
        
        for field in fields:
            if schema_type == "Create" and field.primary:
                continue  # Skip primary key in create schema
            
            python_type = self._get_python_type(field)
            default = ""
            
            if schema_type == "Update":
                # All fields optional in update
                if "None" not in python_type:
                    python_type = f"{python_type} | None"
                default = " = None"
            elif not field.required and not field.primary:
                default = " = None"
            
            field_lines.append(f"    {field.name}: {python_type}{default}")
        
        # Add timestamps for response schema
        if schema_type == "Response" and schema.timestamps:
            field_lines.append("    created_at: datetime")
            field_lines.append("    updated_at: datetime")
        
        class_body = "\n".join(field_lines) if field_lines else "    pass"
        
        return f'''class {schema.name}{schema_type}(BaseModel):
    """Pydantic schema for {schema.name} {schema_type.lower()}."""
{class_body}
    
    class Config:
        from_attributes = True
'''
    
    def generate_router(self, schema: SchemaDefinition, fields: list[FieldDefinition]) -> str:
        """Generate complete CRUD router for a schema."""
        model_name = schema.name
        table_name = schema.table
        route_prefix = f"/{table_name}"
        
        # Find primary key field
        pk_field = next((f for f in fields if f.primary), None)
        pk_name = pk_field.name if pk_field else "id"
        pk_type = self._get_python_type(pk_field) if pk_field else "UUID"
        
        imports = f'''"""Auto-generated CRUD router for {model_name}."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, time
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.models.{model_name.lower()} import {model_name}
from app.core.hooks import hook_registry
'''
        
        # Generate Pydantic schemas
        create_schema = self._generate_pydantic_schema(schema, fields, "Create")
        update_schema = self._generate_pydantic_schema(schema, fields, "Update")
        response_schema = self._generate_pydantic_schema(schema, fields, "Response")
        
        schemas = f"\n{create_schema}\n\n{update_schema}\n\n{response_schema}"
        
        # Generate router
        router_code = f'''
router = APIRouter(prefix="{route_prefix}", tags=["{table_name}"])


@router.post("/", response_model={model_name}Response, status_code=201)
def create_{table_name.rstrip('s')}(
    item: {model_name}Create,
    db: Session = Depends(get_db)
):
    """Create a new {model_name}."""
    # Execute before_create hooks
    data = item.model_dump()
    hook_registry.execute_hooks("before_create", "{model_name}", data=data)
    
    db_item = {model_name}(**data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Execute after_create hooks
    hook_registry.execute_hooks("after_create", "{model_name}", instance=db_item)
    
    return db_item


@router.get("/", response_model=List[{model_name}Response])
def list_{table_name}(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all {table_name} with pagination."""
    items = db.query({model_name}).offset(skip).limit(limit).all()
    return items


@router.get("/{{{pk_name}}}", response_model={model_name}Response)
def get_{table_name.rstrip('s')}(
    {pk_name}: {pk_type},
    db: Session = Depends(get_db)
):
    """Get a single {model_name} by ID."""
    item = db.query({model_name}).filter({model_name}.{pk_name} == {pk_name}).first()
    if not item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return item


@router.put("/{{{pk_name}}}", response_model={model_name}Response)
def update_{table_name.rstrip('s')}(
    {pk_name}: {pk_type},
    item_update: {model_name}Update,
    db: Session = Depends(get_db)
):
    """Update a {model_name}."""
    item = db.query({model_name}).filter({model_name}.{pk_name} == {pk_name}).first()
    if not item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    
    # Store old data for audit hooks
    old_data = {{k: v for k, v in item.__dict__.items() if not k.startswith('_')}}
    
    # Execute before_update hooks
    update_data = item_update.model_dump(exclude_unset=True)
    hook_registry.execute_hooks("before_update", "{model_name}", instance=item, data=update_data)
    
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    # Execute after_update hooks
    hook_registry.execute_hooks("after_update", "{model_name}", instance=item, old_data=old_data)
    
    return item


@router.delete("/{{{pk_name}}}", status_code=204)
def delete_{table_name.rstrip('s')}(
    {pk_name}: {pk_type},
    db: Session = Depends(get_db)
):
    """Delete a {model_name}."""
    item = db.query({model_name}).filter({model_name}.{pk_name} == {pk_name}).first()
    if not item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    
    # Execute before_delete hooks (can abort deletion)
    should_delete = hook_registry.execute_hooks("before_delete", "{model_name}", instance=item)
    
    if should_delete is False:
        # Hook aborted deletion (e.g., soft delete)
        db.commit()  # Commit any changes made by hooks
        return None
    
    # Store instance data for after_delete hooks
    instance_data = {{k: v for k, v in item.__dict__.items() if not k.startswith('_')}}
    
    db.delete(item)
    db.commit()
    
    # Execute after_delete hooks
    hook_registry.execute_hooks("after_delete", "{model_name}", instance_data=instance_data)
    
    return None
'''
        
        return imports + schemas + router_code
    
    def write_router(self, schema: SchemaDefinition, fields: list[FieldDefinition]) -> Path:
        """Generate and write router to file."""
        code = self.generate_router(schema, fields)
        output_file = self.output_dir / f"{schema.name.lower()}.py"
        
        with open(output_file, 'w') as f:
            f.write(code)
        
        return output_file
    
    def generate_all(self, schemas: list[SchemaDefinition], field_map: dict[str, list[FieldDefinition]]) -> list[Path]:
        """Generate all routers and return list of created files."""
        files = []
        for schema in schemas:
            fields = field_map[schema.name]
            file_path = self.write_router(schema, fields)
            files.append(file_path)
        
        # Generate __init__.py to import all routers
        init_code = "# Auto-generated router imports\n"
        init_code += "from fastapi import APIRouter\n\n"
        
        for schema in schemas:
            init_code += f"from .{schema.name.lower()} import router as {schema.name.lower()}_router\n"
        
        init_code += "\n# Combine all routers\n"
        init_code += "api_router = APIRouter()\n"
        for schema in schemas:
            init_code += f"api_router.include_router({schema.name.lower()}_router)\n"
        
        init_file = self.output_dir / "__init__.py"
        with open(init_file, 'w') as f:
            f.write(init_code)
        
        return files
