                                               

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0002_alter_skill_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='category',
            field=models.CharField(choices=[('Backend', 'Бэкенд'), ('Frontend', 'Фронтенд'), ('DevOps', 'DevOps'), ('Data Science', 'Аналитика данных'), ('Mobile', 'Мобильная разработка')], default='Backend', max_length=50),
        ),
    ]
