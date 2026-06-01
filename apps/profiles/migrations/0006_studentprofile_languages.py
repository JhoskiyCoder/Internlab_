                                               

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_studentproject'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='languages',
            field=models.TextField(blank=True, default=''),
        ),
    ]
