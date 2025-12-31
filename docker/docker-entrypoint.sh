#!/bin/bash
set -e

echo "🚀 Starting Backend-in-a-Box..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! pg_isready -h db -U postgres > /dev/null 2>&1; do
    sleep 1
done
echo "✅ Database is ready"

# Generate code from schema
echo "🏗️  Generating backend code..."
python -m generator

# Run migrations
echo "📦 Running database migrations..."
python migrate.py upgrade

echo "🎉 Migrations complete, starting application..."

# Start the application
exec "$@"
