#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Make migrations first to ensure all models are properly registered
echo "Creating migrations..."
python manage.py makemigrations afriapp logistics agro_linker


# Run migrations with verbosity to see detailed output, but skip initial migrations
# to avoid conflicts with existing database schema
echo "Running migrations..."
python manage.py migrate --noinput --verbosity 2 --fake-initial

# Create static directory if it doesn't exist
mkdir -p staticfiles

# Skip collectstatic and just copy the static files directly
echo "Copying static files directly..."
cp -r afriapp/static/* staticfiles/

echo "Build completed successfully!"
