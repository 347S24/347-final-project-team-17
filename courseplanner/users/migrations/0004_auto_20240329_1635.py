# Generated by Django 3.1.1 on 2024-03-29 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20240329_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='expectedGraduationYear',
            field=models.IntegerField(blank=True, default=2024, max_length=5, verbose_name='Name'),
        ),
    ]
