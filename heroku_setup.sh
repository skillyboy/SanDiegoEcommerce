#!/bin/bash
# Heroku setup script for SanDiegoEcommerce

# Install Heroku CLI if not already installed
if ! command -v heroku &> /dev/null; then
    echo "Installing Heroku CLI..."
    curl https://cli-assets.heroku.com/install.sh | sh
else
    echo "Heroku CLI already installed."
fi

# Login to Heroku
echo "Logging in to Heroku..."
heroku login

# Create a new Heroku app
echo "Creating a new Heroku app..."
heroku create

# Get the app name
APP_NAME=$(heroku apps:info | grep "=== " | cut -d' ' -f2)
echo "App name: $APP_NAME"

# Add PostgreSQL addon
echo "Adding PostgreSQL addon..."
heroku addons:create heroku-postgresql:mini

# Set environment variables
echo "Setting environment variables..."
heroku config:set HEROKU_APP_NAME=$APP_NAME
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
heroku config:set DEBUG=False
heroku config:set YOUR_DOMAIN=https://$APP_NAME.herokuapp.com

# Prompt for Stripe keys
echo "Enter your Stripe public key:"
read STRIPE_PUBLIC_KEY
echo "Enter your Stripe secret key:"
read STRIPE_SECRET_KEY
echo "Enter your Stripe webhook secret (optional):"
read STRIPE_WEBHOOK_SECRET

# Set Stripe environment variables
heroku config:set STRIPE_PUBLIC_KEY=$STRIPE_PUBLIC_KEY
heroku config:set STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
if [ ! -z "$STRIPE_WEBHOOK_SECRET" ]; then
    heroku config:set STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET
fi

# Deploy to Heroku
echo "Deploying to Heroku..."
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main

# Run migrations
echo "Running migrations..."
heroku run python manage.py migrate

# Create superuser
echo "Creating superuser..."
heroku run python manage.py createsuperuser

# Collect static files
echo "Collecting static files..."
heroku run python manage.py collectstatic --noinput

echo "Setup complete! Your app is now available at: https://$APP_NAME.herokuapp.com"
