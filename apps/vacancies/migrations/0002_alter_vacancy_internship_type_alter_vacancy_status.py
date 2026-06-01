                                               

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='internship_type',
            field=models.CharField(choices=[('onsite', 'Офис'), ('remote', 'Удаленно'), ('hybrid', 'Гибрид')], default='onsite', max_length=20),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='status',
            field=models.CharField(choices=[('draft', 'Черновик'), ('published', 'Опубликована'), ('closed', 'Закрыта'), ('archived', 'В архиве')], default='draft', max_length=20),
        ),
    ]
