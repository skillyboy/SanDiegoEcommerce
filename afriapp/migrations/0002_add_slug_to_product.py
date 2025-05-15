from django.db import migrations
from django.utils.text import slugify

def generate_product_slugs(apps, schema_editor):
    Product = apps.get_model('afriapp', 'Product')
    for product in Product.objects.all():
        if not product.slug:
            base_slug = slugify(product.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            product.slug = slug
            product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('afriapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(generate_product_slugs),
    ]
