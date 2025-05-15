from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('afriapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='min_purchase',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='product',
            name='max_purchase',
            field=models.PositiveIntegerField(default=20),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
