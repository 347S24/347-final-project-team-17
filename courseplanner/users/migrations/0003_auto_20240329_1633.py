# Generated by Django 3.1.1 on 2024-03-29 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_expectedgraduationyear'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='expectedGraduationYear',
            field=models.IntegerField(default=2024, verbose_name='Expected Graduation Year'),
        ),
    ]