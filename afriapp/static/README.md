# Static Files Organization

## Overview
This directory contains all static files for the African Food San Diego e-commerce website.

## Directory Structure
- `audio/` - Sound files for notifications (success.mp3, info.mp3, error.mp3)
- `css/` - Stylesheets
- `img/` - Images
  - `products/` - Product images
  - `banners/` - Banner images
  - `icons/` - Icon images
  - `flags/` - Flag images
- `js/` - JavaScript files

## Missing Files
The following files were reported as 404 errors and need to be added:

### Images
- `img/produce-2.jpg`
- `img/produce-3.jpg`
- `img/produce-4.jpg`
- `img/featured-1.jpg`
- `img/featured-2.jpg`
- `img/featured-3.jpg`
- `img/cover-25.jpg`
- `img/product-6.jpg`
- `img/newsletter-bg.jpg`
- `img/favicon.png`
- `img/pix.jpg`

### Audio
- `audio/success.mp3`
- `audio/info.mp3`
- `audio/error.mp3`

## jQuery Issue
The website was using jQuery Slim version which doesn't include AJAX functionality. This has been fixed by replacing it with the full version of jQuery.

## How to Add Missing Files
1. Place the missing image files in the appropriate directories
2. Place the missing audio files in the `audio/` directory
3. Run `python manage.py collectstatic` to collect all static files

## Default Image
If a product image is missing, the system will use `img/placeholder.png` as a fallback.
