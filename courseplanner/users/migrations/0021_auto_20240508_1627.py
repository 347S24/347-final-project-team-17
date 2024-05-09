# Generated by Django 3.1.1 on 2024-05-08 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_auto_20240508_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercourse',
            name='semester',
            field=models.CharField(choices=[('FALL', 'Fall'), ('SPRING', 'Spring'), ('SUMMER', 'Summer'), ('WINTER', 'Winter')], max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='usercourse',
            name='year',
            field=models.IntegerField(choices=[(2024, '2024'), (2025, '2025'), (2026, '2026'), (2027, '2027'), (2028, '2028'), (2029, '2029'), (2030, '2030'), (2031, '2031')], null=True),
        ),
    ]
