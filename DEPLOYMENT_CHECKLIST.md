# Deployment Checklist

This document provides a checklist for deploying the SanDiegoEcommerce application to production.

## Pre-Deployment Tasks

- [ ] Run all tests and ensure they pass
- [ ] Set `DEBUG = False` in production settings
- [ ] Generate a new secure `SECRET_KEY` for production
- [ ] Configure proper `ALLOWED_HOSTS` in settings
- [ ] Set up proper database credentials for production
- [ ] Configure Stripe API keys for production environment
- [ ] Set up proper email settings for production
- [ ] Ensure all static files are collected
- [ ] Check for any hardcoded URLs or paths
- [ ] Review security settings (HTTPS, CSRF, etc.)
- [ ] Set up proper logging configuration

## Database Setup

- [ ] Create production database
- [ ] Run migrations on production database
- [ ] Create superuser account
- [ ] Load initial data if needed

## Environment Variables

Ensure the following environment variables are set in your production environment:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to 'False'
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Database connection URL
- `STRIPE_PUBLIC_KEY`: Stripe public key
- `STRIPE_SECRET_KEY`: Stripe secret key
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook secret
- `YOUR_DOMAIN`: Your production domain

## Deployment Options

### Option 1: Heroku Deployment

1. Create a Heroku app
2. Add PostgreSQL add-on
3. Configure environment variables in Heroku dashboard
4. Push code to Heroku
5. Run migrations
6. Create superuser

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY=your_secret_key_here
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
heroku config:set STRIPE_PUBLIC_KEY=your_stripe_public_key
heroku config:set STRIPE_SECRET_KEY=your_stripe_secret_key
heroku config:set STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
heroku config:set YOUR_DOMAIN=https://your-app-name.herokuapp.com
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Option 2: Docker Deployment

1. Build Docker images
2. Push images to container registry
3. Deploy containers to your server
4. Run migrations
5. Create superuser

```bash
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Post-Deployment Tasks

- [ ] Verify the application is running correctly
- [ ] Test all critical flows (account creation, shopping, payment, logistics)
- [ ] Set up monitoring and alerts
- [ ] Configure backups for the database
- [ ] Set up SSL certificate
- [ ] Configure domain name
- [ ] Test payment processing in production mode
- [ ] Verify email sending functionality

## Monitoring and Maintenance

- [ ] Set up application monitoring (e.g., Sentry, New Relic)
- [ ] Configure server monitoring (e.g., Datadog, Prometheus)
- [ ] Set up regular database backups
- [ ] Implement a deployment strategy for future updates
- [ ] Document the deployment process for team members
