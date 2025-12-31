"""Main code generation orchestrator."""
from pathlib import Path
from generator.parser import SchemaParser
from generator.validator import SchemaValidator
from generator.model_gen import ModelGenerator
from generator.api_gen import APIGenerator


def generate_code(schema_dir: str = "app/schema", models_dir: str = "app/models", api_dir: str = "app/api"):
    """Main code generation pipeline."""
    print("🚀 Starting code generation...")
    
    # Step 1: Parse schemas
    print(f"📖 Parsing schemas from {schema_dir}...")
    parser = SchemaParser(schema_dir)
    schemas = parser.parse_all()
    print(f"   Found {len(schemas)} schema(s): {', '.join(s.name for s in schemas)}")
    
    # Step 2: Extract fields and relations
    field_map = {}
    relation_map = {}
    for schema in schemas:
        field_map[schema.name] = parser.get_field_definitions(schema)
        relation_map[schema.name] = parser.get_relations(schema)
    
    # Step 3: Validate schemas
    print("✅ Validating schemas...")
    validator = SchemaValidator()
    try:
        validator.validate_all(schemas, field_map)
        print("   All schemas valid!")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        raise
    
    # Step 4: Generate models
    print(f"🏗️  Generating SQLAlchemy models in {models_dir}...")
    model_gen = ModelGenerator(models_dir)
    model_files = model_gen.generate_all(schemas, field_map, relation_map)
    print(f"   Generated {len(model_files)} model file(s)")
    
    # Step 5: Generate API routers
    print(f"🌐 Generating CRUD routers in {api_dir}...")
    api_gen = APIGenerator(api_dir)
    api_files = api_gen.generate_all(schemas, field_map)
    print(f"   Generated {len(api_files)} router file(s)")
    
    print("✨ Code generation complete!")
    return schemas


if __name__ == "__main__":
    generate_code()
