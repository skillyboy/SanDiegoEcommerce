#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create static directory if it doesn't exist
mkdir -p staticfiles

# Skip collectstatic and just copy the static files directly
echo "Copying static files directly..."
cp -r afriapp/static/* staticfiles/

echo "Build completed successfully!"
