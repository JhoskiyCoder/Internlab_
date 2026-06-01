                                               

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_studentprofile_languages'),
        ('vacancies', '0002_alter_vacancy_internship_type_alter_vacancy_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteVacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_vacancies', to='profiles.studentprofile')),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by_students', to='vacancies.vacancy')),
            ],
            options={
                'ordering': ('-created_at',),
                'unique_together': {('student_profile', 'vacancy')},
            },
        ),
    ]
