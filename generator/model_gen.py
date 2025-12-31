"""Model generator - converts schema AST to SQLAlchemy models."""
from pathlib import Path
from textwrap import indent
from generator.parser import SchemaDefinition, FieldDefinition, RelationDefinition


class ModelGenerator:
    """Generates SQLAlchemy model code from schema definitions."""
    
    TYPE_MAPPING = {
        "string": "String",
        "integer": "Integer",
        "float": "Float",
        "boolean": "Boolean",
        "datetime": "DateTime",
        "date": "Date",
        "time": "Time",
        "uuid": "UUID",
        "text": "Text",
        "json": "JSON",
        "binary": "LargeBinary",
    }
    
    def __init__(self, output_dir: Path | str):
        """Initialize generator with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_sqlalchemy_type(self, field: FieldDefinition) -> str:
        """Convert field type to SQLAlchemy type."""
        sa_type = self.TYPE_MAPPING.get(field.type, "String")
        
        if field.type == "string" and field.max_length:
            return f"String({field.max_length})"
        
        return sa_type
    
    def _generate_field_code(self, field: FieldDefinition) -> str:
        """Generate SQLAlchemy column definition for a field."""
        sa_type = self._get_sqlalchemy_type(field)
        args = [sa_type]
        
        # Add constraints
        if field.primary:
            args.append("primary_key=True")
            if field.type == "uuid":
                args.append("default=uuid.uuid4")
        if field.unique:
            args.append("unique=True")
        if not field.nullable:
            args.append("nullable=False")
        if field.index:
            args.append("index=True")
        if field.default is not None:
            if isinstance(field.default, str):
                args.append(f'default="{field.default}"')
            elif isinstance(field.default, bool):
                args.append(f"default={field.default}")
            else:
                args.append(f"default={field.default}")
        
        return f"    {field.name} = Column({', '.join(args)})"
    
    def _generate_relation_code(self, relation: RelationDefinition, schema_name: str) -> str:
        """Generate SQLAlchemy relationship definition."""
        target = relation.target
        
        if relation.type == "one_to_many":
            back_pop = relation.back_populates or f"{schema_name.lower()}s"
            return f'    {target.lower()}s = relationship("{target}", back_populates="{back_pop}")'
        
        elif relation.type == "many_to_one":
            back_pop = relation.back_populates or f"{target.lower()}"
            fk = relation.foreign_key or f"{target.lower()}s.id"
            return (
                f'    {target.lower()}_id = Column(UUID, ForeignKey("{fk}"))\n'
                f'    {target.lower()} = relationship("{target}", back_populates="{back_pop}")'
            )
        
        elif relation.type == "many_to_many":
            # Simplified many-to-many (would need association table)
            back_pop = relation.back_populates or f"{schema_name.lower()}s"
            return f'    {target.lower()}s = relationship("{target}", secondary="{schema_name.lower()}_{target.lower()}", back_populates="{back_pop}")'
        
        return ""
    
    def generate_model(self, schema: SchemaDefinition, fields: list[FieldDefinition], relations: list[RelationDefinition]) -> str:
        """Generate complete model code for a schema."""
        imports = [
            "from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Time, Text, JSON, LargeBinary, ForeignKey, UUID",
            "from sqlalchemy.orm import relationship",
            "from datetime import datetime",
            "from app.core.database import Base",
            "import uuid",
        ]
        
        # Generate field definitions
        field_lines = [self._generate_field_code(field) for field in fields]
        
        # Add timestamps if enabled
        timestamp_fields = []
        if schema.timestamps:
            timestamp_fields = [
                "    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)",
                "    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)",
            ]
        
        # Add soft delete if enabled
        soft_delete_field = []
        if schema.soft_delete:
            soft_delete_field = ["    deleted_at = Column(DateTime, nullable=True)"]
        
        # Generate relationships
        relation_lines = [self._generate_relation_code(rel, schema.name) for rel in relations]
        
        # Combine all parts
        class_body = "\n".join(
            field_lines + timestamp_fields + soft_delete_field + relation_lines
        )
        
        model_code = f'''"""Auto-generated model for {schema.name}."""
{chr(10).join(imports)}


class {schema.name}(Base):
    """SQLAlchemy model for {schema.name}."""
    __tablename__ = "{schema.table}"

{class_body}
'''
        
        return model_code
    
    def write_model(self, schema: SchemaDefinition, fields: list[FieldDefinition], relations: list[RelationDefinition]) -> Path:
        """Generate and write model to file."""
        code = self.generate_model(schema, fields, relations)
        output_file = self.output_dir / f"{schema.name.lower()}.py"
        
        with open(output_file, 'w') as f:
            f.write(code)
        
        return output_file
    
    def generate_all(self, schemas: list[SchemaDefinition], field_map: dict[str, list[FieldDefinition]], relation_map: dict[str, list[RelationDefinition]]) -> list[Path]:
        """Generate all models and return list of created files."""
        files = []
        for schema in schemas:
            fields = field_map[schema.name]
            relations = relation_map[schema.name]
            file_path = self.write_model(schema, fields, relations)
            files.append(file_path)
        
        # Generate __init__.py to import all models
        init_code = "# Auto-generated model imports\n"
        for schema in schemas:
            init_code += f"from .{schema.name.lower()} import {schema.name}\n"
        
        init_file = self.output_dir / "__init__.py"
        with open(init_file, 'w') as f:
            f.write(init_code)
        
        return files
