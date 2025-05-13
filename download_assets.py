"""
Script to download sample images and audio files for the African Food San Diego e-commerce website.
This script will download:
- Product images (produce-2.jpg, produce-3.jpg, etc.)
- Featured images (featured-1.jpg, featured-2.jpg, etc.)
- Audio files (success.mp3, info.mp3, error.mp3)
"""

import os
import requests
import shutil
from pathlib import Path

# Create directories if they don't exist
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Download a file from a URL
def download_file(url, destination):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        with open(destination, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        print(f"Downloaded: {destination}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

# Main directories
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'afriapp' / 'static'
IMG_DIR = STATIC_DIR / 'img'
AUDIO_DIR = STATIC_DIR / 'audio'

# Ensure directories exist
ensure_dir(IMG_DIR)
ensure_dir(AUDIO_DIR)

# Image URLs - using placeholder images from Unsplash for African food/produce
IMAGE_URLS = {
    # Product images
    'produce-2.jpg': 'https://images.unsplash.com/photo-1604329756574-bda1f2cada6f?q=80&w=600&auto=format&fit=crop',
    'produce-3.jpg': 'https://images.unsplash.com/photo-1509358271058-acd22cc93898?q=80&w=600&auto=format&fit=crop',
    'produce-4.jpg': 'https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?q=80&w=600&auto=format&fit=crop',

    # Featured images
    'featured-1.jpg': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=600&auto=format&fit=crop',
    'featured-2.jpg': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=600&auto=format&fit=crop',
    'featured-3.jpg': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=600&auto=format&fit=crop',

    # Other images
    'cover-25.jpg': 'https://images.unsplash.com/photo-1543362906-acfc16c67564?q=80&w=800&auto=format&fit=crop',
    'product-6.jpg': 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?q=80&w=600&auto=format&fit=crop',
    'newsletter-bg.jpg': 'https://images.unsplash.com/photo-1590779033100-9f60a05a013d?q=80&w=800&auto=format&fit=crop',
}

# Audio URLs - using sample notification sounds from soundbible.com
AUDIO_URLS = {
    'success.mp3': 'https://soundbible.com/grab.php?id=2204&type=mp3',  # Ding sound
    'info.mp3': 'https://soundbible.com/grab.php?id=2156&type=mp3',     # Notification sound
    'error.mp3': 'https://soundbible.com/grab.php?id=1540&type=mp3',    # Error sound
}

# Download images
print("Downloading images...")
for filename, url in IMAGE_URLS.items():
    download_file(url, IMG_DIR / filename)

# Download audio files
print("\nDownloading audio files...")
for filename, url in AUDIO_URLS.items():
    download_file(url, AUDIO_DIR / filename)

print("\nDownload complete! Run 'python manage.py collectstatic' to update your static files.")
