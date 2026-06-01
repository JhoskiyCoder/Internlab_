                                               

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
