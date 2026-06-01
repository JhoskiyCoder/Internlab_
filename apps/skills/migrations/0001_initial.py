                                               

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('category', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='StudentSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_entries', to='skills.skill')),
                ('student_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skills', to='profiles.studentprofile')),
            ],
            options={
                'ordering': ('student_profile', 'skill'),
                'unique_together': {('student_profile', 'skill')},
            },
        ),
    ]
