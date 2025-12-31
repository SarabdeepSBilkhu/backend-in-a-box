"""Schema parser - converts YAML schema definitions to internal AST."""
from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, Field


class FieldDefinition(BaseModel):
    """Definition of a single field in a schema."""
    name: str
    type: str
    primary: bool = False
    unique: bool = False
    required: bool = False
    default: Any = None
    nullable: bool = True
    max_length: int | None = None
    index: bool = False


class RelationDefinition(BaseModel):
    """Definition of a relationship between models."""
    type: str  # one_to_many, many_to_one, many_to_many
    target: str
    back_populates: str | None = None
    foreign_key: str | None = None


class SchemaDefinition(BaseModel):
    """Complete schema definition for a model."""
    name: str
    table: str
    fields: dict[str, dict[str, Any]]
    relations: list[dict[str, Any]] = Field(default_factory=list)
    soft_delete: bool = False
    timestamps: bool = True


class SchemaParser:
    """Parser for YAML schema files."""
    
    def __init__(self, schema_dir: Path | str):
        """Initialize parser with schema directory."""
        self.schema_dir = Path(schema_dir)
    
    def parse_file(self, file_path: Path) -> SchemaDefinition:
        """Parse a single YAML schema file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return SchemaDefinition(**data)
    
    def parse_all(self) -> list[SchemaDefinition]:
        """Parse all YAML files in the schema directory."""
        schemas = []
        for file_path in self.schema_dir.glob("*.yaml"):
            schemas.append(self.parse_file(file_path))
        return schemas
    
    def get_field_definitions(self, schema: SchemaDefinition) -> list[FieldDefinition]:
        """Convert field dict to FieldDefinition objects."""
        fields = []
        for field_name, field_config in schema.fields.items():
            fields.append(
                FieldDefinition(
                    name=field_name,
                    **field_config
                )
            )
        return fields
    
    def get_relations(self, schema: SchemaDefinition) -> list[RelationDefinition]:
        """Convert relation dict to RelationDefinition objects."""
        return [RelationDefinition(**rel) for rel in schema.relations]
