"""Schema validator - validates schema definitions for correctness."""
from typing import Any
from generator.parser import SchemaDefinition, FieldDefinition


class ValidationError(Exception):
    """Raised when schema validation fails."""
    pass


class SchemaValidator:
    """Validates schema definitions."""
    
    VALID_TYPES = {
        "string", "integer", "float", "boolean", "datetime", "date", "time",
        "uuid", "text", "json", "binary"
    }
    
    VALID_RELATION_TYPES = {"one_to_many", "many_to_one", "many_to_many"}
    
    def __init__(self):
        """Initialize validator."""
        self.schemas: dict[str, SchemaDefinition] = {}
    
    def validate_field_type(self, field: FieldDefinition) -> None:
        """Validate that field type is supported."""
        if field.type not in self.VALID_TYPES:
            raise ValidationError(
                f"Invalid field type '{field.type}' for field '{field.name}'. "
                f"Valid types: {', '.join(sorted(self.VALID_TYPES))}"
            )
    
    def validate_primary_key(self, schema: SchemaDefinition, fields: list[FieldDefinition]) -> None:
        """Validate that schema has exactly one primary key."""
        primary_keys = [f for f in fields if f.primary]
        if len(primary_keys) == 0:
            raise ValidationError(f"Schema '{schema.name}' must have a primary key")
        if len(primary_keys) > 1:
            raise ValidationError(
                f"Schema '{schema.name}' has multiple primary keys: "
                f"{', '.join(f.name for f in primary_keys)}"
            )
    
    def validate_required_nullable(self, field: FieldDefinition) -> None:
        """Validate that required fields are not nullable."""
        if field.required and field.nullable and not field.primary:
            raise ValidationError(
                f"Field '{field.name}' cannot be both required and nullable"
            )
    
    def validate_relations(self, schema: SchemaDefinition) -> None:
        """Validate relationship definitions."""
        for relation in schema.relations:
            rel_type = relation.get("type")
            if rel_type not in self.VALID_RELATION_TYPES:
                raise ValidationError(
                    f"Invalid relation type '{rel_type}' in schema '{schema.name}'. "
                    f"Valid types: {', '.join(sorted(self.VALID_RELATION_TYPES))}"
                )
            
            target = relation.get("target")
            if not target:
                raise ValidationError(
                    f"Relation in schema '{schema.name}' missing 'target' field"
                )
    
    def validate_schema(self, schema: SchemaDefinition, fields: list[FieldDefinition]) -> None:
        """Validate a complete schema definition."""
        # Validate each field
        for field in fields:
            self.validate_field_type(field)
            self.validate_required_nullable(field)
        
        # Validate primary key
        self.validate_primary_key(schema, fields)
        
        # Validate relations
        self.validate_relations(schema)
    
    def validate_all(self, schemas: list[SchemaDefinition], field_map: dict[str, list[FieldDefinition]]) -> None:
        """Validate all schemas and cross-references."""
        # Store schemas for cross-validation
        self.schemas = {s.name: s for s in schemas}
        
        # Validate each schema
        for schema in schemas:
            fields = field_map[schema.name]
            self.validate_schema(schema, fields)
        
        # Validate relation targets exist
        for schema in schemas:
            for relation in schema.relations:
                target = relation.get("target")
                if target and target not in self.schemas:
                    raise ValidationError(
                        f"Relation target '{target}' in schema '{schema.name}' does not exist"
                    )
