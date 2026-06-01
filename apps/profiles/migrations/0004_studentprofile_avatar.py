from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("profiles", "0003_studentprofile_phone_number")]
    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="avatar",
            field=models.ImageField(
                blank=True, null=True, upload_to="avatars/students/"
            ),
        )
    ]
