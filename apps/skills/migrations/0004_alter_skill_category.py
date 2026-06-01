from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("skills", "0003_alter_skill_category")]
    operations = [
        migrations.AlterField(
            model_name="skill",
            name="category",
            field=models.CharField(
                choices=[
                    ("Backend", "Бэкенд"),
                    ("Frontend", "Фронтенд"),
                    ("DevOps", "DevOps"),
                    ("Data Science", "Аналитика данных"),
                    ("Machine Learning", "Машинное обучение"),
                    ("Core Skills", "Базовые навыки"),
                    ("Mobile", "Мобильная разработка"),
                ],
                default="Backend",
                max_length=50,
            ),
        )
    ]
