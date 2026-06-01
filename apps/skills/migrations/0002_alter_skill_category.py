                                               

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='category',
            field=models.CharField(choices=[('Backend', 'Backend'), ('Frontend', 'Frontend'), ('DevOps', 'DevOps'), ('Data Science', 'Data Science'), ('Mobile', 'Mobile')], default='Backend', max_length=50),
        ),
    ]
