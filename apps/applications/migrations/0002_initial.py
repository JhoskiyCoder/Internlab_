                                               

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vacancies', '0001_initial'),
        ('applications', '0001_initial'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='profiles.studentprofile'),
        ),
        migrations.AddField(
            model_name='application',
            name='vacancy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='vacancies.vacancy'),
        ),
        migrations.AlterUniqueTogether(
            name='application',
            unique_together={('student', 'vacancy')},
        ),
    ]
