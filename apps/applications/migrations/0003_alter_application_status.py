from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("applications", "0002_initial")]
    operations = [
        migrations.AlterField(
            model_name="application",
            name="status",
            field=models.CharField(
                choices=[
                    ("submitted", "Подана"),
                    ("reviewing", "На рассмотрении"),
                    ("accepted", "Принята"),
                    ("rejected", "Отклонена"),
                ],
                default="submitted",
                max_length=20,
            ),
        )
    ]
