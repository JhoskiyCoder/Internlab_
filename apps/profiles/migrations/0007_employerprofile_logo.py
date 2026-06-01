                                               

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_studentprofile_languages'),
    ]

    operations = [
        migrations.AddField(
            model_name='employerprofile',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/employers/'),
        ),
    ]
